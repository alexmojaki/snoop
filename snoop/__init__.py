'''
PySnooper - Never use print for debugging again

Usage:

    import snoop

    @snoop.snoop()
    def your_function(x):
        ...

A log will be written to stderr showing the lines executed and variables
changed in the decorated function.

For more information, see https://github.com/cool-RR/PySnooper
'''

from .tracer import Tracer as snoop, pp, spy
from .installer import install
from .variables import Attrs, Exploding, Indices, Keys
import collections
import sys

__VersionInfo = collections.namedtuple('VersionInfo',
                                       ('major', 'minor', 'micro'))

__version__ = '0.1.0'
__version_info__ = __VersionInfo(*(map(int, __version__.split('.'))))

sys.modules['snoop'] = snoop  # make the module callable

# Add all the attributes to the 'module' so things can be imported normally
for key, value in list(globals().items()):
    if key in 'collections sys __VersionInfo key value':
        # Avoid polluting the namespace
        continue

    setattr(snoop, key, value)
