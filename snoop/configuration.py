import inspect
import os
import pprint
import sys
import threading
from io import open

import six

import snoop as package
from snoop.formatting import DefaultFormatter
from snoop.pp_module import PP
from snoop.tracer import Spy, Tracer
from snoop.utils import Mapping, QuerySet, Sequence, Set
from snoop.utils import builtins as builtins_module
from snoop.utils import ensure_tuple, is_pathlike, shitcode

try:
    # Enable ANSI escape codes in Windows 10
    import ctypes

    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    can_color = True
except Exception:
    can_color = os.name != 'nt'


def install(
        builtins=True,
        snoop="snoop",
        pp="pp",
        spy="spy",
        out=None,
        prefix='',
        columns='time',
        overwrite=False,
        color=None,
        enabled=True,
        watch_extras=(),
        replace_watch_extras=None,
        formatter_class=DefaultFormatter,
        pformat=None,
):
    """
    Configure output, enable or disable, and add names to builtins. Parameters:

    - builtins: set to False to not add any names to builtins,
        so importing will still be required.
    - snoop, pp, and spy: set to other strings
        to choose the names of these functions in builtins
    - `out`: determines the output destination. By default this is stderr. You can also pass:
        - A string or a `Path` object to write to a file at that location. By default this always will append to the file. Pass `overwrite=True` to clear the file initially.
        - Anything with a `write` method, e.g. `sys.stdout` or a file object.
        - Any callable with a single string argument, e.g. `logger.info`.
    - `color`: determines whether the output includes escape characters to display colored text in the console. If you see weird characters in your output, your console doesn't support colors, so pass `color=False`.
        - Code is syntax highlighted using [Pygments](http://pygments.org/), and this argument is passed as the style. You can choose a different color scheme by passing a string naming a style (see [this gallery](https://help.farbox.com/pygments.html)) or a style class. The default style is monokai.
        - By default this parameter is set to `out.isatty()`, which is usually true for stdout and stderr but will be false if they are redirected or piped. Pass `True` or a style if you want to force coloring.
        - To see colors in the PyCharm Run window, edit the Run Configuration and tick "Emulate terminal in output console".
    - `prefix`: Pass a string to start all snoop lines with that string so you can grep for them easily.
    - `columns`: This specifies the columns at the start of each output line. You can pass a string with the names of built in columns separated by spaces or commas. These are the available columns:
        - `time`: The current time. This is the only column by default.
        - `thread`: The name of the current thread.
        - `thread_ident`: The [identifier](https://docs.python.org/3/library/threading.html#threading.Thread.ident) of the current thread, in case thread names are not unique.
        - `file`: The filename (not the full path) of the current function.
        - `full_file`: The full path to the file (also shown anyway when the function is called).
        - `function`: The name of the current function.
        - `function_qualname`: The qualified name of the current function.

        If you want a custom column, please open an issue to tell me what you're interested in! In the meantime, you can pass a list, where the elements are either strings or callables. The callables should take one argument, which will be an `Event` object. It has attributes `frame`, `event`, and `arg`, as specified in [`sys.settrace()`](https://docs.python.org/3/library/sys.html#sys.settrace), and other attributes which may change.
    - `pformat`: set the pretty formatting function `pp` uses. Default is to use the first of `prettyprinter.pformat`, `pprintpp.pformat` and `pprint.pformat` that can be imported.
    """

    if builtins:
        setattr(builtins_module, snoop, package.snoop)
        setattr(builtins_module, pp, package.pp)
        setattr(builtins_module, spy, package.spy)
    config = Config(
        out=out,
        prefix=prefix,
        columns=columns,
        overwrite=overwrite,
        color=color,
        enabled=enabled,
        watch_extras=watch_extras,
        replace_watch_extras=replace_watch_extras,
        formatter_class=formatter_class,
        pformat=pformat,
    )
    package.snoop.config = config
    package.pp.config = config
    package.spy.config = config


class Config(object):
    """"
    If you need more control than the global `install` function, e.g. if you want to write to several different files in one process, you can create a `Config` object, e.g: `config = snoop.Config(out=filename)`. Then `config.snoop`, `config.pp` and `config.spy` will use that configuration rather than the global one.

    The arguments are the same as the arguments of `install()` relating to output configuration and `enabled`.
    """

    def __init__(
            self,
            out=None,
            prefix='',
            columns='time',
            overwrite=False,
            color=None,
            enabled=True,
            watch_extras=(),
            replace_watch_extras=None,
            formatter_class=DefaultFormatter,
            pformat=None,
    ):
        if can_color:
            if color is None:
                isatty = getattr(out or sys.stderr, 'isatty', lambda: False)
                color = bool(isatty())
        else:
            color = False

        self.write = get_write_function(out, overwrite)
        self.formatter = formatter_class(prefix, columns, color)
        self.enabled = enabled

        if pformat is None:
            try:
                from prettyprinter import pformat
            except Exception:
                try:
                    from pprintpp import pformat
                except Exception:
                    from pprint import pformat

        self.pformat = pformat

        self.pp = PP(self)

        class ConfiguredTracer(Tracer):
            config = self

        self.snoop = ConfiguredTracer
        self.spy = Spy(self)

        self.last_frame = None
        self.thread_local = threading.local()

        if replace_watch_extras is not None:
            self.watch_extras = ensure_tuple(replace_watch_extras)
        else:
            self.watch_extras = (len_shape_watch, dtype_watch) + ensure_tuple(watch_extras)


def len_shape_watch(source, value):
    try:
        shape = value.shape
    except Exception:
        pass
    else:
        if not inspect.ismethod(shape):
            return '{}.shape'.format(source), shape

    if isinstance(value, QuerySet):
        # Getting the length of a Django queryset evaluates it
        return None

    length = len(value)
    if (
            (isinstance(value, six.string_types)
             and length < 50) or
            (isinstance(value, (Mapping, Set, Sequence))
             and length == 0)
    ):
        return None

    return 'len({})'.format(source), length


def dtype_watch(source, value):
    dtype = value.dtype
    if not inspect.ismethod(dtype):
        return '{}.dtype'.format(source), dtype


def get_write_function(output, overwrite):
    is_path = (
        isinstance(output, six.string_types)
        or is_pathlike(output)
    )
    if is_path:
        return FileWriter(output, overwrite).write
    elif callable(output):
        write = output
    else:
        def write(s):
            stream = output

            if stream is None:
                stream = sys.stderr

            try:
                stream.write(s)
            except UnicodeEncodeError:
                # God damn Python 2
                stream.write(shitcode(s))

            getattr(stream, "flush", lambda: None)()

    return write


class FileWriter(object):
    def __init__(self, path, overwrite):
        self.path = six.text_type(path)
        self.overwrite = overwrite

    def write(self, s):
        with open(self.path, 'w' if self.overwrite else 'a', encoding='utf-8') as f:
            f.write(s)
        self.overwrite = False
