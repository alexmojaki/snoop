import functools
import inspect
import os
import re
import sys
import threading
from collections import OrderedDict

import six
# noinspection PyUnresolvedReferences
from cheap_repr import cheap_repr, find_repr_function

from snoop.utils import my_cheap_repr, NO_ASTTOKENS, ArgDefaultDict, iscoroutinefunction, \
    truncate_list, ensure_tuple, is_comprehension_frame, no_args_decorator
from .formatting import Event, Source
from .variables import CommonVariable, Exploding, BaseVariable

find_repr_function(six.text_type).maxparts = 100
find_repr_function(six.binary_type).maxparts = 100
find_repr_function(object).maxparts = 100
find_repr_function(int).maxparts = 999999
cheap_repr.suppression_threshold = 999999


class FrameInfo(object):
    def __init__(self, frame):
        self.frame = frame
        self.local_reprs = {}
        self.last_line_no = frame.f_lineno
        self.comprehension_variables = OrderedDict()
        self.source = Source.for_frame(frame)
        self.is_generator = frame.f_code.co_flags & inspect.CO_GENERATOR
        self.had_exception = False
        if is_comprehension_frame(frame):
            self.comprehension_type = (
                    re.match(r'<(\w+)comp>', frame.f_code.co_name).group(1).title()
                    + u' comprehension'
            )
        else:
            self.comprehension_type = ''

    def update_variables(self, watch, watch_extras, event):
        self.last_line_no = self.frame.f_lineno
        old_local_reprs = self.local_reprs
        self.local_reprs = OrderedDict(
            (source, my_cheap_repr(value))
            for source, value in
            self.get_local_reprs(watch, watch_extras)
        )

        if self.comprehension_type:
            for name, value_repr in self.local_reprs.items():
                values = self.comprehension_variables.setdefault(name, [])
                if not values or values[-1] != value_repr:
                    values.append(value_repr)
                    values[:] = truncate_list(values, 11)
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

        result_items = sorted(
            frame.f_locals.items(),
            key=lambda key_value: vars_order.index(key_value[0])
        )

        for variable in watch:
            result_items += sorted(variable.items(frame))

        for source, value in result_items:
            yield source, value
            for extra in watch_extras:
                try:
                    pair = extra(source, value)
                except Exception:
                    pass
                else:
                    if pair is not None:
                        assert len(pair) == 2, "Watch extra must return pair or None"
                        yield pair


thread_global = threading.local()
internal_directories = (os.path.dirname((lambda: 0).__code__.co_filename),)

try:
    # noinspection PyUnresolvedReferences
    import birdseye
except ImportError:
    pass
else:
    internal_directories += (os.path.dirname(birdseye.__file__),)


class TracerMeta(type):
    def __new__(mcs, *args, **kwargs):
        result = super(TracerMeta, mcs).__new__(mcs, *args, **kwargs)
        result.default = result()
        return result

    def __call__(cls, *args, **kwargs):
        if no_args_decorator(args, kwargs):
            return cls.default(args[0])
        else:
            return super(TracerMeta, cls).__call__(*args, **kwargs)

    def __enter__(self):
        return self.default.__enter__(context=1)

    def __exit__(self, *args):
        return self.default.__exit__(*args, context=1)


@six.add_metaclass(TracerMeta)
class Tracer(object):
    def __init__(
            self,
            watch=(),
            watch_explode=(),
            depth=1,
    ):
        self.watch = [
            v if isinstance(v, BaseVariable) else CommonVariable(v)
            for v in ensure_tuple(watch)
        ] + [
            v if isinstance(v, BaseVariable) else Exploding(v)
            for v in ensure_tuple(watch_explode)
        ]
        self.frame_infos = ArgDefaultDict(FrameInfo)
        self.depth = depth
        assert self.depth >= 1
        self.target_codes = set()
        self.target_frames = set()

    def __call__(self, function):
        if iscoroutinefunction(function):
            raise NotImplementedError("coroutines are not supported, sorry!")

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

        if inspect.isgeneratorfunction(function):
            return generator_wrapper
        else:
            return simple_wrapper

    def __enter__(self, context=0):
        if not self.config.enabled:
            return

        calling_frame = sys._getframe(context + 1)
        if not self._is_internal_frame(calling_frame):
            calling_frame.f_trace = self.trace
            self.target_frames.add(calling_frame)
            self.config.last_frame = calling_frame
            self.trace(calling_frame, 'enter', None)

        stack = thread_global.__dict__.setdefault('original_trace_functions', [])
        stack.append(sys.gettrace())
        sys.settrace(self.trace)

    def __exit__(self, exc_type, exc_value, exc_traceback, context=0):
        if not self.config.enabled:
            return

        stack = thread_global.original_trace_functions
        sys.settrace(stack.pop())
        calling_frame = sys._getframe(context + 1)
        self.trace(calling_frame, 'exit', None)
        self.target_frames.discard(calling_frame)
        self.frame_infos.pop(calling_frame, None)

    def _is_internal_frame(self, frame):
        return frame.f_code.co_filename.startswith(internal_directories)
    
    def _is_traced_frame(self, frame):
        return frame.f_code in self.target_codes or frame in self.target_frames

    def trace(self, frame, event, arg):
        if not self._is_traced_frame(frame):
            if (
                    self.depth == 1
                    or self._is_internal_frame(frame)
            ) and not is_comprehension_frame(frame):
                return None
            else:
                candidate = frame
                i = 0
                while True:
                    if is_comprehension_frame(candidate):
                        candidate = candidate.f_back
                        continue
                    i += 1
                    if self._is_traced_frame(candidate):
                        break
                    candidate = candidate.f_back
                    if i >= self.depth or candidate is None or self._is_internal_frame(candidate):
                        return None

        thread_local = self.config.thread_local
        thread_local.__dict__.setdefault('depth', -1)
        frame_info = self.frame_infos[frame]
        if event in ('call', 'enter'):
            thread_local.depth += 1
        elif self.config.last_frame and self.config.last_frame is not frame:
            line_no = frame_info.last_line_no
            trace_event = Event(frame_info, event, arg, thread_local.depth, line_no=line_no)
            line = self.config.formatter.format_line_only(trace_event)
            self.config.write(line)

        if event == 'exception':
            frame_info.had_exception = True

        self.config.last_frame = frame

        trace_event = Event(frame_info, event, arg, thread_local.depth)
        if not (frame.f_code.co_name == '<genexpr>' and event not in ('return', 'exception')):
            trace_event.variables = frame_info.update_variables(
                self.watch,
                self.config.watch_extras,
                event,
            )

        if event in ('return', 'exit'):
            del self.frame_infos[frame]
            thread_local.depth -= 1

        formatted = self.config.formatter.format(trace_event)
        self.config.write(formatted)

        return self.trace


class Spy(object):
    def __init__(self, config):
        self.config = config

    def __call__(self, *args, **kwargs):
        if NO_ASTTOKENS:
            raise Exception("birdseye doesn't support this version of Python")

        try:
            import birdseye
        except ImportError:
            raise Exception("You must install birdseye separately to use spy: pip install birdseye")

        # Decorator without parentheses
        if no_args_decorator(args, kwargs):
            return self._trace(args[0])

        # Decorator with parentheses and perhaps arguments
        def decorator(func):
            return self._trace(func, *args, **kwargs)

        return decorator

    def _trace(self, func, *args, **kwargs):
        # noinspection PyUnresolvedReferences
        from birdseye import eye

        traced = eye(func)
        traced = self.config.snoop(*args, **kwargs)(traced)

        @functools.wraps(func)
        def wrapper(*func_args, **func_kwargs):
            if self.config.enabled:
                final_func = traced
            else:
                final_func = func

            return final_func(*func_args, **func_kwargs)

        return wrapper
