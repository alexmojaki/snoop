'''Python 2/3 compatibility'''

import abc
import ast
import os
import inspect

if hasattr(abc, 'ABC'):
    ABC = abc.ABC
else:
    class ABC(object):
        """Helper class that provides a standard way to create an ABC using
        inheritance.
        """
        __metaclass__ = abc.ABCMeta
        __slots__ = ()

if hasattr(os, 'PathLike'):
    PathLike = os.PathLike
else:
    class PathLike(ABC):
        """Abstract base class for implementing the file system path protocol."""

        @abc.abstractmethod
        def __fspath__(self):
            """Return the file system path representation of the object."""
            raise NotImplementedError

        @classmethod
        def __subclasshook__(cls, subclass):
            return (
                    hasattr(subclass, '__fspath__') or
                    # Make a concession for older `pathlib` versions:g
                    (hasattr(subclass, 'open') and
                     'path' in subclass.__name__.lower())
            )

try:
    iscoroutinefunction = inspect.iscoroutinefunction
except AttributeError:
    iscoroutinefunction = lambda whatever: False  # Lolz

try:
    try_statement = ast.Try
except AttributeError:
    try_statement = ast.TryExcept

try:
    builtins = __import__("__builtin__")
except ImportError:
    builtins = __import__("builtins")
