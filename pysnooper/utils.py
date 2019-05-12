# Copyright 2019 Ram Rachum and collaborators.
# This program is distributed under the MIT license.

from .third_party import six

MAX_VARIABLE_LENGTH = 100
MAX_EXCEPTION_LENGTH = 200


file_reading_errors = (
    IOError,
    OSError,
    ValueError # IronPython weirdness.
)



def shitcode(s):
    return ''.join(
        (c if (0 < ord(c) < 256) else '?') for c in s
    )


def get_shortish_repr(item):
    try:
        r = repr(item)
    except Exception:
        r = 'REPR FAILED'
    r = r.replace('\r', '').replace('\n', '')
    r = truncate(r, MAX_VARIABLE_LENGTH)
    return r


def truncate(string, max_length):
    if len(string) > max_length:
        left = (max_length - 3) // 2
        right = max_length - 3 - left
        string = u'{}...{}'.format(string[:left], string[-right:])
    return string


def ensure_tuple(x):
    if isinstance(x, six.string_types):
        x = (x,)
    return tuple(x)



