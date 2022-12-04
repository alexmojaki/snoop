import ast
import inspect
import traceback
import warnings
from copy import deepcopy
from threading import current_thread
from uuid import uuid4

from executing import future_flags, only

from snoop.formatting import Event, Source
from snoop.tracer import FrameInfo
from snoop.utils import (NO_ASTTOKENS, FormattedValue, builtins,
                         optional_numeric_label, pp_name_prefix)


class PP(object):
    def __init__(self, config):
        self.config = config

    def __call__(self, *args):
        if self.config.enabled:
            PPEvent(self, args, deep=False)

        if len(args) == 1:
            return args[0]
        else:
            return args

    def deep(self, arg):
        if not is_deep_arg(arg):
            raise TypeError("Argument must be a lambda without arguments")

        if self.config.enabled:
            return PPEvent(self, [arg], deep=True).returns

        return arg()


class PPEvent(object):
    def __init__(self, pp_object, args, deep):
        self.config = pp_object.config
        self.args = args
        depth = getattr(self.config.thread_local, 'depth', 0)
        frame = inspect.currentframe().f_back.f_back
        self.event = Event(FrameInfo(frame), 'log', None, depth)
        formatted = self.config.formatter.format_log(self.event)
        self.config.write(formatted)

        self.returns = None
        try:
            assert not NO_ASTTOKENS
            self.call = call = Source.executing(frame).node
            assert isinstance(call, ast.Call)
            assert len(args) == len(call.args)
        except Exception:
            if deep:
                self.returns = args[0] = args[0]()
            for i, arg in enumerate(args):
                self.write_placeholder(i, arg)
        else:
            if deep:
                call_arg = only(call.args)
                assert isinstance(call_arg, ast.Lambda), "You must pass a lambda DIRECTLY to pp.deep, not as a result of any other expression"
                self.returns = self.deep_pp(call_arg.body, frame)
            else:
                self.plain_pp(args, call.args)

    def write(self, source, value, depth=0):
        if depth == 0:
            value_string = self.config.pformat(value)
        else:
            try:
                value_string = repr(value)
            except Exception as e:
                exception_string = ''.join(
                    traceback.format_exception_only(type(e), e)
                ).strip()
                value_string = '<Exception in repr(): {}>'.format(exception_string)

        formatted = self.config.formatter.format_log_value(
            self.event, source, value_string, depth)
        self.config.write(formatted)

    def write_node(self, node, value, depth=0):
        source = self.event.source.get_text_with_indentation(node)
        self.write(source, value, depth=depth)

    def write_placeholder(self, i, arg):
        source = '<argument{}>'.format(optional_numeric_label(i, self.args))
        return self.write(source, arg)

    def plain_pp(self, args, call_args):
        for i, (call_arg, arg) in enumerate(zip(call_args, args)):
            try:
                self.write_node(call_arg, arg)
            except Exception:
                self.write_placeholder(i, arg)

    def deep_pp(self, call_arg, frame):
        stack = []
        thread = current_thread()

        def before_expr(tree_index):
            node = self.event.source.nodes[tree_index]
            if thread == current_thread():
                stack.append(node)
            return node

        before_expr.name = pp_name_prefix + 'before_' + uuid4().hex

        def after_expr(node, value):
            if thread == current_thread():
                assert node is stack.pop()

            try:
                ast.literal_eval(node)
                is_obvious = True
            except ValueError:
                is_obvious = (
                    isinstance(node, ast.Name)
                    and getattr(builtins, node.id, object()) == value
                )

            if not is_obvious:
                self.write_node(node, value, depth=node._depth - call_arg._depth)
            return value

        after_expr.name = pp_name_prefix + 'after_' + uuid4().hex

        new_node = deepcopy(call_arg)
        new_node = NodeVisitor(before_expr.name, after_expr.name).visit(new_node)
        expr = ast.Expression(new_node)
        ast.copy_location(expr, new_node)
        code = compile(
            expr,
            frame.f_code.co_filename,
            'eval',
            dont_inherit=True,
            flags=future_flags & frame.f_code.co_flags,
        )
        frame.f_globals[before_expr.name] = before_expr
        frame.f_globals[after_expr.name] = after_expr
        try:
            return eval(code, frame.f_globals, frame.f_locals)
        except Exception as e:
            if stack:
                last_node = stack[-1]
                self.write_node(
                    last_node,
                    DirectRepr('!!! {}!'.format(e.__class__.__name__)),
                    last_node._depth - call_arg._depth,
                )
            raise
        finally:
            frame.f_globals[before_expr.name] = lambda x: x
            frame.f_globals[after_expr.name] = lambda node, value: value


class DirectRepr(str):
    def __repr__(self):
        return self


try:
    getargspec = inspect.getfullargspec
except AttributeError:
    getargspec = inspect.getargspec


def is_deep_arg(x):
    return (
        inspect.isfunction(x)
        and x.__code__.co_name == '<lambda>'
        and not any(getargspec(x))
    )


class NodeVisitor(ast.NodeTransformer):
    """
    This does the AST modifications that call the hooks.
    """

    def __init__(self, before_name, after_name):
        self.before_name = before_name
        self.after_name = after_name

    def generic_visit(self, node):
        # type: (ast.AST) -> ast.AST
        if (isinstance(node, ast.expr) and
                not (hasattr(node, "ctx") and not isinstance(node.ctx, ast.Load)) and
                not isinstance(node, getattr(ast, 'Starred', ()))):
            return self.visit_expr(node)
        return super(NodeVisitor, self).generic_visit(node)

    def visit_expr(self, node):
        # type: (ast.expr) -> ast.Call
        """
        each expression e gets wrapped like this:
            _treetrace_hidden_after_expr(_treetrace_hidden_before_expr(_tree_index), e)

        where the _treetrace_* functions are the corresponding methods with the
        TreeTracerBase and traced_file arguments already filled in (see _trace_methods_dict)
        """

        before_marker = ast.Call(
            func=ast.Name(id=self.before_name,
                          ctx=ast.Load()),
            args=[ast.Num(node._tree_index)],
            keywords=[],
        )

        ast.copy_location(before_marker, node)

        if isinstance(node, FormattedValue):
            arg = node
        else:
            arg = super(NodeVisitor, self).generic_visit(node)

        after_marker = ast.Call(
            func=ast.Name(id=self.after_name,
                          ctx=ast.Load()),
            args=[
                before_marker,
                arg,
            ],
            keywords=[],
        )
        ast.copy_location(after_marker, node)
        ast.fix_missing_locations(after_marker)

        return after_marker
