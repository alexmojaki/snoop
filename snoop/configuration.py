import os
import sys
import threading
from io import open

import six

import snoop as package
from snoop.formatting import DefaultFormatter
from snoop.utils import builtins as builtins_module, is_pathlike, shitcode
from snoop.tracer import Spy, Tracer
from snoop.pp_module import PP

try:
    import colorama
except ImportError:
    colorama = None


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
        formatter_class=DefaultFormatter,
        use_colorama=True,
):
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
        formatter_class=formatter_class,
        use_colorama=use_colorama,
    )
    package.snoop.config = config
    package.pp.config = config
    package.spy.config = config


class Config(object):
    def __init__(
            self,
            out=None,
            prefix='',
            columns='time',
            overwrite=False,
            color=None,
            enabled=True,
            formatter_class=DefaultFormatter,
            use_colorama=True,
    ):
        isatty = getattr(out or sys.stderr, 'isatty', lambda: False)()
        if color is None:
            color = bool(isatty)
        use_colorama = use_colorama and color and colorama and isatty and os.name == 'nt'

        self.write = get_write_function(out, overwrite, use_colorama)
        self.formatter = formatter_class(prefix, columns, color)
        self.enabled = enabled
        self.pp = PP(self)

        class ConfiguredTracer(Tracer):
            config = self

        self.snoop = ConfiguredTracer
        self.spy = Spy(self)

        self.last_frame = None
        self.thread_local = threading.local()


def get_write_function(output, overwrite, use_colorama):
    is_path = (
        isinstance(output, six.string_types)
        or is_pathlike(output)
    )
    if overwrite and not is_path:
        raise Exception('`overwrite=True` can only be used when writing '
                        'content to file.')

    if is_path:
        return FileWriter(output, overwrite).write
    elif callable(output):
        write = output
    else:
        def write(s):
            stream = output

            if stream is None:
                stream = sys.stderr

            if stream in (sys.stderr, sys.stdout) and use_colorama:
                stream = colorama.AnsiToWin32(stream, convert=True)

            try:
                stream.write(s)
            except UnicodeEncodeError:
                # God damn Python 2
                output.write(shitcode(s))
    return write


class FileWriter(object):
    def __init__(self, path, overwrite):
        self.path = six.text_type(path)
        self.overwrite = overwrite

    def write(self, s):
        with open(self.path, 'w' if self.overwrite else 'a', encoding='utf-8') as f:
            f.write(s)
        self.overwrite = False
