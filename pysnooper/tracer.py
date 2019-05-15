# Copyright 2019 Ram Rachum and collaborators.
# This program is distributed under the MIT license.

import collections
import functools
import inspect
import re
import sys
import threading

import six
from cheap_repr import cheap_repr

from .formatting import DefaultFormatter, Event
from . import utils, pycompat
from .variables import CommonVariable, Exploding, BaseVariable

ipython_filename_pattern = re.compile('^<ipython-input-([0-9]+)-.*>$')


def get_local_reprs(frame, watch=()):
    code = frame.f_code
    vars_order = code.co_varnames + code.co_cellvars + code.co_freevars + tuple(frame.f_locals.keys())

    result_items = [(key, cheap_repr(value)) for key, value in frame.f_locals.items()]
    result_items.sort(key=lambda key_value: vars_order.index(key_value[0]))
    result = collections.OrderedDict(result_items)

    for variable in watch:
        result.update(sorted(variable.items(frame)))
    return result


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
        with open(self.path, 'w' if self.overwrite else 'a') as output_file:
            output_file.write(s)
        self.overwrite = False


thread_global = threading.local()


class Tracer(object):
    '''
    Snoop on the function, writing everything it's doing to stderr.

    This is useful for debugging.

    When you decorate a function with `@pysnooper.snoop()`
    or wrap a block of code in `with pysnooper.snoop():`, you'll get a log of
    every line that ran in the function and a play-by-play of every local
    variable that changed.

    If stderr is not easily accessible for you, you can redirect the output to
    a file::

        @pysnooper.snoop('/my/log/file.log')

    See values of some expressions that aren't local variables::

        @pysnooper.snoop(watch=('foo.bar', 'self.x["whatever"]'))

    Expand values to see all their attributes or items of lists/dictionaries:

        @pysnooper.snoop(watch_explode=('foo', 'self'))

    (see Advanced Usage in the README for more control)

    Show snoop lines for functions that your function calls::

        @pysnooper.snoop(depth=2)

    Start all snoop lines with a prefix, to grep for them easily::

        @pysnooper.snoop(prefix='ZZZ ')
    '''

    formatter_class = DefaultFormatter
    
    def __init__(
            self,
            output=None,
            watch=(),
            watch_explode=(),
            depth=1,
            prefix='',
            columns='time',
            overwrite=False,
    ):
        self._write = get_write_function(output, overwrite)

        self.watch = [
            v if isinstance(v, BaseVariable) else CommonVariable(v)
            for v in utils.ensure_tuple(watch)
         ] + [
             v if isinstance(v, BaseVariable) else Exploding(v)
             for v in utils.ensure_tuple(watch_explode)
        ]
        self.frame_to_local_reprs = {}
        self.depth = depth
        assert self.depth >= 1
        self.target_codes = set()
        self.target_frames = set()
        self.thread_local = threading.local()
        self.formatter = self.formatter_class(prefix, columns)

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

    def __enter__(self):
        calling_frame = inspect.currentframe().f_back
        if not self._is_internal_frame(calling_frame):
            calling_frame.f_trace = self.trace
            self.target_frames.add(calling_frame)

        stack = self.thread_local.__dict__.setdefault('original_trace_functions', [])
        stack.append(sys.gettrace())
        sys.settrace(self.trace)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        stack = self.thread_local.original_trace_functions
        sys.settrace(stack.pop())
        calling_frame = inspect.currentframe().f_back
        self.target_frames.discard(calling_frame)
        self.frame_to_local_reprs.pop(calling_frame, None)

    def _is_internal_frame(self, frame):
        return frame.f_code.co_filename == Tracer.__enter__.__code__.co_filename

    def trace(self, frame, event, arg):

        ### Checking whether we should trace this line: #######################
        #                                                                     #
        # We should trace this line either if it's in the decorated function,
        # or the user asked to go a few levels deeper and we're within that
        # number of levels deeper.

        if not (frame.f_code in self.target_codes or frame in self.target_frames):
            if self.depth == 1:
                # We did the most common and quickest check above, because the
                # trace function runs so incredibly often, therefore it's
                # crucial to hyper-optimize it for the common case.
                return None
            elif self._is_internal_frame(frame):
                return None
            else:
                _frame_candidate = frame
                for i in range(1, self.depth):
                    _frame_candidate = _frame_candidate.f_back
                    if _frame_candidate is None:
                        return None
                    elif _frame_candidate.f_code in self.target_codes or _frame_candidate in self.target_frames:
                        break
                else:
                    return None

        thread_global.__dict__.setdefault('depth', -1)
        if event == 'call':
            thread_global.depth += 1

        #                                                                     #
        ### Finished checking whether we should trace this line. ##############

        ### Reporting newish and modified variables: ##########################
        #                                                                     #
        old_local_reprs = self.frame_to_local_reprs.get(frame, {})
        self.frame_to_local_reprs[frame] = local_reprs = \
                                       get_local_reprs(frame, watch=self.watch)

        trace_event = Event(frame, event, arg, thread_global.depth)

        for name, value_repr in local_reprs.items():
            if name not in old_local_reprs or old_local_reprs[name] != value_repr:
                trace_event.variables.append((name, value_repr))

        if event == 'return':
            del self.frame_to_local_reprs[frame]
            thread_global.depth -= 1
        
        formatted = self.formatter.format(trace_event)
        self._write(formatted)
        
        #                                                                     #
        ### Finished newish and modified variables. ###########################

        return self.trace
