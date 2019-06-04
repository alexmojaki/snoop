import sys
import threading

import six

import snoop as package
from snoop import pycompat, utils
from snoop.formatting import DefaultFormatter
from snoop.pycompat import builtins as builtins_module


def install(builtins=True, snoop="snoop", pp="pp", spy="spy", **kwargs):
    if builtins:
        setattr(builtins_module, snoop, package.snoop)
        setattr(builtins_module, pp, package.pp)
        setattr(builtins_module, spy, package.spy)
    config = Config(**kwargs)
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
    ):
        from .tracer import Spy, Tracer
        from .pp_module import PP

        if color is None:
            color = (
                    out is None and sys.stderr.isatty()
                    or getattr(out, 'isatty', lambda: False)()
            )

        self.write = get_write_function(out, overwrite)
        self.formatter = formatter_class(prefix, columns, color)
        self.enabled = enabled
        self.pp = PP(self)

        class ConfiguredTracer(Tracer):
            config = self

        self.snoop = ConfiguredTracer
        self.spy = Spy(self)

        self.last_frame = None
        self.thread_local = threading.local()


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
