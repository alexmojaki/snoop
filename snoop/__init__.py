'''
Usage:

    import snoop

    @snoop
    def your_function(x):
        ...

A log will be written to stderr showing the lines executed and variables
changed in the decorated function.

For more information, see https://github.com/alexmojaki/snoop
'''

import collections
import sys

from .configuration import Config, install
from .variables import Attrs, Exploding, Indices, Keys

__VersionInfo = collections.namedtuple('VersionInfo',
                                       ('major', 'minor', 'micro'))

try:
    from .version import __version__

except ImportError:  # pragma: no cover
    # version.py is auto-generated with the git tag when building
    __version__ = "???"

try:
    __version_info__ = __VersionInfo(*(map(int, __version__.split('.'))))
except ValueError:
    __version_info__ = None


config = Config()
snoop = config.snoop
pp = config.pp
spy = config.spy
install = staticmethod(install)

sys.modules['snoop'] = snoop  # make the module callable

# Add all the attributes to the 'module' so things can be imported normally
for key, value in list(globals().items()):
    if key in 'collections sys __VersionInfo key value config':
        # Avoid polluting the namespace
        continue

    setattr(snoop, key, value)
