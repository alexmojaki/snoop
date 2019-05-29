from littleutils import setattrs

from snoop.pycompat import builtins as builtins_module
import snoop as package
from snoop.tracer import Defaults


def install(builtins=True, snoop="snoop", pp="pp", spy="spy", **kwargs):
    if builtins:
        setattr(builtins_module, snoop, package.snoop)
        setattr(builtins_module, pp, package.pp)
        setattr(builtins_module, spy, package.spy)
    setattrs(Defaults, **kwargs)
