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

from .configuration import install, Config
from .variables import Attrs, Exploding, Indices, Keys
import collections
import sys

__VersionInfo = collections.namedtuple('VersionInfo',
                                       ('major', 'minor', 'micro'))

__version__ = '0.2.3'
__version_info__ = __VersionInfo(*(map(int, __version__.split('.'))))

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
