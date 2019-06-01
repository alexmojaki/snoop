import ast
import collections
import functools
import inspect
import sys
import threading
from io import open

import six
# noinspection PyUnresolvedReferences
from cheap_repr import cheap_repr

from .bird import deep_pp
from . import utils, pycompat
from .formatting import DefaultFormatter, Event, Source
from .variables import CommonVariable, Exploding, BaseVariable

try:
    from django.db.models import QuerySet
except ImportError:
    class QuerySet(object):
        pass


def get_write_function(output, overwrite):
    is_path = isinstance(output, (pycompat.PathLike, str))
    if overwrite and not is_path:
        raise Exception('`overwrite=True` can only be used when writing '
                        'content to file.')
    if output is None:
        def write(s):
            stderr = sys.stderr
            try:
                stderr.write(s)
            except UnicodeEncodeError:
                # God damn Python 2
                stderr.write(utils.shitcode(s))
    elif is_path:
        return FileWriter(output, overwrite).write
    elif callable(output):
        write = output
    else:
        write = output.write
    return write


class FileWriter(object):
    def __init__(self, path, overwrite):
        self.path = six.text_type(path)
        self.overwrite = overwrite

    def write(self, s):
        with open(self.path, 'w' if self.overwrite else 'a', encoding='utf-8') as f:
            f.write(s)
        self.overwrite = False


class FrameInfo(object):
    def __init__(self, frame):
        self.frame = frame
        self.local_reprs = {}
        self.last_line_no = frame.f_lineno
        self.comprehension_variables = collections.OrderedDict()

    def update_variables(self, watch, watch_extras, event):
        self.last_line_no = self.frame.f_lineno
        old_local_reprs = self.local_reprs
        self.local_reprs = self.get_local_reprs(watch, watch_extras)

        if utils.is_comprehension_frame(self.frame):
            for name, value_repr in self.local_reprs.items():
                values = self.comprehension_variables.setdefault(name, [])
                if not values or values[-1] != value_repr:
                    values.append(value_repr)
                    values[:] = utils.truncate_list(values, 11)
            if event in ('return', 'exception'):
                return [
                    (name, ', '.join(values))
                    for name, values in self.comprehension_variables.items()
                ]
            else:
                return []

        variables = []
        for name, value_repr in self.local_reprs.items():
            if name not in old_local_reprs or old_local_reprs[name] != value_repr:
                variables.append((name, value_repr))
        return variables

    def get_local_reprs(self, watch, watch_extras):
        frame = self.frame
        code = frame.f_code
        vars_order = code.co_varnames + code.co_cellvars + code.co_freevars + tuple(frame.f_locals.keys())

        result_items = [(key, value) for key, value in frame.f_locals.items()]
        result_items.sort(key=lambda key_value: vars_order.index(key_value[0]))

        for variable in watch:
            result_items += sorted(variable.items(frame))

        result = collections.OrderedDict()
        for source, value in result_items:
            result[source] = cheap_repr(value)
            for extra in watch_extras:

                try:
                    pair = extra(source, value)
                except Exception:
                    pass
                else:
                    if pair is not None:
                        extra_source, extra_value = pair
                        result[extra_source] = extra_value

        return result


def len_watch(source, value):
    if isinstance(value, QuerySet):
        # Getting the length of a Django queryset evaluates it
        return None

    length = len(value)
    if (
            (isinstance(value, six.string_types)
             and length < 50) or
            (isinstance(value, (collections.Mapping, collections.Set, collections.Sequence))
             and length == 0)
    ):
        return None

    return 'len({})'.format(source), length


def shape_watch(source, value):
    shape = value.shape
    if inspect.ismethod(shape):
        return None
    return '{}.shape'.format(source), shape


thread_global = threading.local()


class Defaults:
    out = None
    watch = ()
    watch_explode = ()
    watch_extras = ()
    replace_watch_extras = None
    depth = 1
    prefix = ''
    columns = 'time'
    overwrite = False
    color = None


class TracerMeta(type):
    def __new__(mcs, *args, **kwargs):
        result = super(TracerMeta, mcs).__new__(mcs, *args, **kwargs)
        result.default = result()
        return result

    def __enter__(self):
        return self.default.__enter__(context=1)

    def __exit__(self, *args):
        return self.default.__exit__(*args, context=1)


@six.add_metaclass(TracerMeta)
class Tracer(object):
    '''
    Snoop on the function, writing everything it's doing to stderr.

    This is useful for debugging.

    When you decorate a function with `@snoop()`
    or wrap a block of code in `with snoop():`, you'll get a log of
    every line that ran in the function and a play-by-play of every local
    variable that changed.

    If stderr is not easily accessible for you, you can redirect the output to
    a file::

        @snoop('/my/log/file.log')

    See values of some expressions that aren't local variables::

        @snoop(watch=('foo.bar', 'self.x["whatever"]'))

    Expand values to see all their attributes or items of lists/dictionaries:

        @snoop(watch_explode=('foo', 'self'))

    (see Advanced Usage in the README for more control)

    Show snoop lines for functions that your function calls::

        @snoop(depth=2)

    Start all snoop lines with a prefix, to grep for them easily::

        @snoop(prefix='ZZZ ')
    '''

    formatter_class = DefaultFormatter
    
    def __init__(
            self,
            out=None,
            watch=None,
            watch_explode=None,
            watch_extras=None,
            replace_watch_extras=None,
            depth=None,
            prefix=None,
            columns=None,
            overwrite=None,
            color=None,
    ):
        if out is None:
            out = Defaults.out
        if watch is None:
            watch = Defaults.watch
        if watch_explode is None:
            watch_explode = Defaults.watch_explode
        if watch_extras is None:
            watch_extras = Defaults.watch_extras
        if replace_watch_extras is None:
            replace_watch_extras = Defaults.replace_watch_extras
        if depth is None:
            depth = Defaults.depth
        if prefix is None:
            prefix = Defaults.prefix
        if columns is None:
            columns = Defaults.columns
        if overwrite is None:
            overwrite = Defaults.overwrite
        if color is None:
            color = Defaults.color

        if color is None:
            color = (
                    out is None and sys.stderr.isatty()
                    or getattr(out, 'isatty', lambda: False)()
            )

        self._write = get_write_function(out, overwrite)

        self.watch = [
            v if isinstance(v, BaseVariable) else CommonVariable(v)
            for v in utils.ensure_tuple(watch)
         ] + [
             v if isinstance(v, BaseVariable) else Exploding(v)
             for v in utils.ensure_tuple(watch_explode)
        ]
        if replace_watch_extras is not None:
            self.watch_extras = utils.ensure_tuple(replace_watch_extras)
        else:
            self.watch_extras = (len_watch, shape_watch) + utils.ensure_tuple(watch_extras)
        self.frame_infos = {}
        self.last_frame = None
        self.depth = depth
        assert self.depth >= 1
        self.target_codes = set()
        self.target_frames = set()
        self.thread_local = threading.local()
        self.formatter = self.formatter_class(prefix, columns, color)

    def __call__(self, function):
        self.target_codes.add(function.__code__)

        @functools.wraps(function)
        def simple_wrapper(*args, **kwargs):
            with self:
                return function(*args, **kwargs)

        @functools.wraps(function)
        def generator_wrapper(*args, **kwargs):
            gen = function(*args, **kwargs)
            method, incoming = gen.send, None
            while True:
                with self:
                    try:
                        outgoing = method(incoming)
                    except StopIteration:
                        return
                try:
                    method, incoming = gen.send, (yield outgoing)
                except Exception as e:
                    method, incoming = gen.throw, e

        if pycompat.iscoroutinefunction(function):
            # return decorate(function, coroutine_wrapper)
            raise NotImplementedError
        elif inspect.isgeneratorfunction(function):
            return generator_wrapper
        else:
            return simple_wrapper

    def __enter__(self, context=0):
        calling_frame = sys._getframe(context + 1)
        if not self._is_internal_frame(calling_frame):
            calling_frame.f_trace = self.trace
            self.target_frames.add(calling_frame)
            self.last_frame = calling_frame
            self.trace(calling_frame, 'enter', None)

        stack = self.thread_local.__dict__.setdefault('original_trace_functions', [])
        stack.append(sys.gettrace())
        sys.settrace(self.trace)

    def __exit__(self, exc_type, exc_value, exc_traceback, context=0):
        stack = self.thread_local.original_trace_functions
        sys.settrace(stack.pop())
        calling_frame = sys._getframe(context + 1)
        self.trace(calling_frame, 'exit', None)
        self.target_frames.discard(calling_frame)
        self.frame_infos.pop(calling_frame, None)

    def _is_internal_frame(self, frame):
        return frame.f_code.co_filename == Tracer.__enter__.__code__.co_filename

    def trace(self, frame, event, arg):
        if not (frame.f_code in self.target_codes or frame in self.target_frames):
            if (
                    self.depth == 1
                    or self._is_internal_frame(frame)
            ) and not utils.is_comprehension_frame(frame):
                return None
            else:
                candidate = frame
                i = 0
                while True:
                    if utils.is_comprehension_frame(candidate):
                        candidate = candidate.f_back
                        continue
                    i += 1
                    if candidate.f_code in self.target_codes or candidate in self.target_frames:
                        break
                    candidate = candidate.f_back
                    if i >= self.depth or candidate is None:
                        return None

        thread_global.__dict__.setdefault('depth', -1)
        frame_info = self.frame_infos.setdefault(frame, FrameInfo(frame))
        if event in ('call', 'enter'):
            thread_global.depth += 1
        elif self.last_frame and self.last_frame is not frame:
            line_no = self.frame_infos[frame].last_line_no
            trace_event = Event(frame, event, arg, thread_global.depth, line_no=line_no)
            line = self.formatter.format_line_only(trace_event)
            self._write(line)
        
        self.last_frame = frame

        trace_event = Event(frame, event, arg, thread_global.depth, last_line_no=frame_info.last_line_no)
        if not (frame.f_code.co_name == '<genexpr>' and event not in ('return', 'exception')):
            trace_event.variables = frame_info.update_variables(self.watch, self.watch_extras, event)

        if event in ('return', 'exit'):
            del self.frame_infos[frame]
            thread_global.depth -= 1
        
        formatted = self.formatter.format(trace_event)
        self._write(formatted)

        return self.trace


def pp(*args):
    frame = inspect.currentframe().f_back
    depth = getattr(thread_global, 'depth', 0)
    event = Event(frame, 'log', None, depth)

    try:
        ast_tokens = event.source.asttokens()
        call = Source.executing_node(frame)
        arg_sources = []
        for call_arg, arg in zip(call.args, args):
            if isinstance(call_arg, ast.Lambda):
                arg_sources.extend(deep_pp(event, call_arg, frame))
            else:
                arg_sources.append((ast_tokens.get_text(call_arg).strip(), arg, 0))
    except Exception:  # TODO narrow
        arg_sources = zip([''] * len(args), args, [0] * len(args))

    tracer = Tracer.default
    formatted = tracer.formatter.format_log(event, arg_sources)
    tracer._write(formatted)

    if len(args) == 1:
        return args[0]
    else:
        return args


def spy(*args, **kwargs):
    from birdseye import eye

    def decorator(func):
        func = eye(func)
        func = Tracer(*args, **kwargs)(func)
        return func

    return decorator
