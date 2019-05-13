# Copyright 2019 Ram Rachum and collaborators.
# This program is distributed under the MIT license.

import six

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


def truncate(string, max_length):
    if len(string) > max_length:
        left = (max_length - 3) // 2
        right = max_length - 3 - left
        string = u'{}...{}'.format(string[:left], string[-right:])
    return string


def ensure_tuple(x):
    if isinstance(x, six.string_types):
        x = x.replace(',', ' ').split()
    if not isinstance(x, (list, set, tuple)):
        x = (x,)
    return tuple(x)



