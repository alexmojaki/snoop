import ast
import inspect
import opcode
import re
import threading
import traceback
from collections import defaultdict
from datetime import datetime

import executing_node
import six
# noinspection PyUnresolvedReferences
from cheap_repr import cheap_repr
from colorama import Fore, Style

from snoop.pycompat import try_statement
from snoop.utils import ensure_tuple, short_filename, is_comprehension_frame, with_needed_parentheses


class StatementsDict(dict):
    def __init__(self, source):
        super(StatementsDict, self).__init__()
        self.source = source

    def __missing__(self, key):
        try:
            statements = self.source.statements_at_line(key)
        except IndexError:
            result = None
        else:
            if len(statements) == 1:
                result = statements[0]
            else:
                result = None
        self[key] = result
        return result


class Source(executing_node.Source):
    def __init__(self, *args, **kwargs):
        super(Source, self).__init__(*args, **kwargs)
        if self.text:
            self.lines = self.text.splitlines()
        else:
            self.lines = defaultdict(lambda: u'SOURCE IS UNAVAILABLE')
        self.statements = StatementsDict(self)
        self.nodes = []
        self.tree._depth = 0
        for node in ast.walk(self.tree):
            node._tree_index = len(self.nodes)
            self.nodes.append(node)
            for child in ast.iter_child_nodes(node):
                child._depth = node._depth + 1


    @classmethod
    def for_frame(cls, frame):
        try:
            return super(Source, cls).for_frame(frame)
        except Exception:
            return cls('', '', '')


class Event(object):
    def __init__(self, frame, event, arg, depth, line_no=None, last_line_no=None):
        self.frame = frame
        self.event = event
        self.arg = arg
        self.depth = depth

        self.variables = []
        self.source = Source.for_frame(frame)
        if line_no is None:
            line_no = frame.f_lineno
        self.line_no = line_no
        self.last_line_no = last_line_no
        code = frame.f_code

        code_byte = code.co_code[frame.f_lasti]
        if not isinstance(code_byte, int):
            code_byte = ord(code_byte)
        self.opname = opcode.opname[code_byte]

        self.is_generator = code.co_flags & inspect.CO_GENERATOR
        if is_comprehension_frame(frame):
            self.comprehension_type = (
                    re.match(r'<(\w+)comp>', code.co_name).group(1).title()
                    + u' comprehension'
            )
        else:
            self.comprehension_type = ''

        if self.event == 'call' and self.source_line.lstrip().startswith('@'):
            # If a function decorator is found, skip lines until an actual
            # function definition is found.
            while True:
                self.line_no += 1
                try:
                    if self.source_line.lstrip().startswith('def'):
                        break
                except IndexError:
                    self.line_no = self.frame.lineno
                    break

    @property
    def source_line(self):
        return self.source.lines[self.line_no - 1]


def highlight_python(code):
    return code
    # TODO
    # import pygments
    # from pygments.formatters.terminal256 import Terminal256Formatter
    # from pygments.lexers.python import PythonLexer
    # return pygments.highlight(
    #     code,
    #     PythonLexer(),
    #     Terminal256Formatter(),
    # ).rstrip()


class DefaultFormatter(object):
    datetime_format = None

    def __init__(self, prefix='', columns='time', color=False):
        prefix = six.text_type(prefix)
        if prefix and prefix == prefix.rstrip():
            prefix += ' '
        self.prefix = prefix
        self.columns = [
            column if callable(column) else
            getattr(self, '{}_column'.format(column))
            for column in ensure_tuple(columns, split=True)
        ]
        self.column_widths = dict.fromkeys(self.columns, 0)
        if color:
            self.c = Colors
        else:
            self.c = NoColors()
            
    def thread_column(self, _event):
        return threading.current_thread().name

    def thread_ident_column(self, _event):
        return threading.current_thread().ident

    def time_column(self, _event):
        datetime_format = self.datetime_format or '%H:%M:%S.%f'
        result = datetime.now().strftime(datetime_format)
        if self.datetime_format is None:
            result = result[:-4]
        return result

    def file_column(self, event):
        return short_filename(event.frame.f_code)

    def function_column(self, event):
        return event.frame.f_code.co_name

    def full_prefix(self, event):
        return u'{c.grey}{self.prefix}{indent}{columns} {c.reset}'.format(
            c=self.c,
            self=self,
            indent=event.depth * u'    ',
            columns=self.columns_string(event),
        )

    def format(self, event):
        lines = []
        dots = ''
        statement_start_lines = []

        if event.event in ('call', 'enter'):
            if event.comprehension_type:
                lines += ['{type}:'.format(
                    type=event.comprehension_type)]
            else:
                if event.is_generator:
                    if event.opname == 'YIELD_VALUE':
                        description = 'Re-enter generator'
                    else:
                        description = 'Start generator'
                elif event.event == 'call':
                    description = 'Call to'
                else:
                    description = 'Enter with block in'
                lines += [
                    u'{c.cyan}>>> {description} {c.reset}{name}{c.cyan} in {c.reset}File "{filename}", line {lineno}'.format(
                        name=event.frame.f_code.co_name,
                        filename=_get_filename(event),
                        lineno=event.line_no,
                        c=self.c,
                        description=description,
                    )]

        statements = event.source.statements
        last_statement = statements[event.last_line_no]
        last_source_line = ''
        if last_statement:
            last_lineno = last_statement.lineno
            last_source_line = event.source.lines[last_lineno - 1]
            spaces = get_leading_spaces(last_source_line)
            dots = spaces.replace(' ', '.').replace('\t', '....')
            if event.event != 'call':
                this_statement = statements[event.line_no]

                if (
                        this_statement != last_statement and
                        this_statement.lineno != event.line_no and
                        not isinstance(this_statement, try_statement)
                ):
                    original_line_no = event.line_no
                    for n in range(this_statement.lineno, original_line_no):
                        event.line_no = n
                        statement_start_lines.append(self.format_event(event))
                    event.line_no = original_line_no

        for var in event.variables:
            if ('{} = {}'.format(*var) != last_source_line.strip()
                    and not (
                            isinstance(last_statement, ast.FunctionDef)
                            and not last_statement.decorator_list
                            and var[0] == last_statement.name
                    )
            ):
                lines += self.format_variable(var, dots, event.comprehension_type)
        
        if event.event == 'return':
            # If a call ends due to an exception, we still get a 'return' event
            # with arg = None. This seems to be the only way to tell the difference
            # https://stackoverflow.com/a/12800909/2482744
            if (event.arg is None
                    and event.opname not in ('RETURN_VALUE', 'YIELD_VALUE')):
                lines += [u'{c.red}!!! Call ended by exception{c.reset}'.format(c=self.c)]
            elif event.comprehension_type:
                value = highlight_python(cheap_repr(event.arg))
                lines += indented_lines(u'Result: ', value)
            else:
                lines += self.format_return_value(event)
        elif event.event == 'exception':
            exception_string = ''.join(traceback.format_exception_only(*event.arg[:2]))
            lines += [
                u'{c.red}!!! {line}{c.reset}'.format(
                    c=self.c,
                    line=line,
                )
                for line in exception_string.splitlines()
            ]
            lines += self.format_executing_node_exception(event)
        elif event.event == 'enter':
            pass
        elif event.event == 'exit':
            lines += [u'{c.green}<<< Exit with block in {func}{c.reset}'.format(
                c=self.c,
                func=event.frame.f_code.co_name,
            )]
        else:
            if not (event.comprehension_type and event.event == 'line'):
                lines += statement_start_lines + [self.format_event(event)]

        return self.format_lines(event, lines)

    def format_executing_node_exception(self, event):
        try:
            call = Source.executing_node(event.frame)
            if not isinstance(call, ast.Call):
                return []
            
            if any(
                    getattr(call, attr, None)
                    for attr in 'args keywords starargs kwargs'.split()
            ):
                args_source = '...'
            else:
                args_source = ''
    
            source = '{func}({args})'.format(
                func=with_needed_parentheses(event.source.asttokens().get_text(call.func)),
                args=args_source,
            )
            plain_prefix = '!!! When calling: '
            prefix = '{c.red}{}{c.reset}'.format(plain_prefix, c=self.c)
            return indented_lines(
                prefix,
                source,
                plain_prefix=plain_prefix
            )
        except Exception:
            return []

    def columns_string(self, event):
        column_strings = []
        for column in self.columns:
            string = six.text_type(column(event))
            width = self.column_widths[column] = max(
                self.column_widths[column],
                len(string),
            )
            column_strings.append(string.ljust(width))
        return u' '.join(column_strings)

    def format_event(self, entry):
        return u'{c.grey}{line_no:4}{c.reset} | {source_line}'.format(
            source_line=highlight_python(entry.source_line),
            c=self.c,
            **entry.__dict__
        )

    def format_variable(self, entry, dots, is_comprehension):
        name, value = entry
        if name.startswith('.') and name[1:].isdigit():
            description = 'Iterating over'
        elif is_comprehension:
            description = 'Values of {name}:'.format(name=name)
        else:
            description = '{name} ='.format(name=name)
        prefix = u'......{dots} {description} '.format(
            description=description,
            dots=dots,
        )
        return indented_lines(prefix, highlight_python(value))

    def format_return_value(self, event):
        value = highlight_python(cheap_repr(event.arg))
        plain_prefix = u'<<< {description} value from {func}: '.format(
            description='Yield' if event.opname == 'YIELD_VALUE' else 'Return',
            func=event.frame.f_code.co_name,
        )
        prefix = u'{c.green}{}{c.reset}'.format(
            plain_prefix,
            c=self.c,
        )
        return indented_lines(prefix, value, plain_prefix=plain_prefix)

    def format_line_only(self, event):
        return self.format_lines(event, [self.format_event(event)])

    def format_log(self, event, values):
        lines = ['LOG:']
        for source, value, depth in values:
            value = cheap_repr(value)
            string = highlight_python('{} = {}'.format(source, value))
            lines += [u'....{} {}'.format(depth * 4 * '.', line)
                      for line in string.splitlines()]
        return self.format_lines(event, lines)

    def format_lines(self, event, lines):
        prefix = self.full_prefix(event)
        return ''.join([
            (
                    prefix
                    + line
                    + u'\n'
            )
            for line in lines
        ])

def get_leading_spaces(s):
    return s[:len(s) - len(s.lstrip())]


def _get_filename(event):
    return event.frame.f_code.co_filename


class NoColors(object):
    def __getattr__(self, item):
        return ''


class Colors(object):
    grey = Fore.LIGHTBLACK_EX
    red = Fore.RED + Style.BRIGHT
    green = Fore.GREEN + Style.BRIGHT
    cyan = Fore.CYAN + Style.BRIGHT
    reset = Style.RESET_ALL


def indented_lines(prefix, string, plain_prefix=None):
    lines = six.text_type(string).splitlines()
    return [prefix + lines[0]] + [
        ' ' * len(plain_prefix or prefix) + line
        for line in lines[1:]
    ]
