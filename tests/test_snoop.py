from __future__ import print_function

import io
import os
import re
import sys
import traceback
from importlib import import_module
from tempfile import mkstemp
from threading import current_thread

import pytest
import six
from cheap_repr import cheap_repr, register_repr
from cheap_repr.utils import safe_qualname
from littleutils import file_to_string, group_by_key_func, string_to_file

# Hide 3rd party pretty-printing modules
sys.modules['prettyprinter'] = {}
sys.modules['pprintpp'] = {}

from snoop import formatting, install, spy
from snoop.configuration import Config
from snoop.pp_module import is_deep_arg
from snoop.utils import (NO_ASTTOKENS, NO_BIRDSEYE, PYPY, needs_parentheses,
                         truncate_list, truncate_string)

formatting._get_filename = lambda _: "/path/to_file.py"

install()

tests_dir = os.path.dirname(__file__)
cheap_repr.raise_exceptions = True


@register_repr(type(cheap_repr))
def repr_function(func, _helper):
    return '<function %s at %#x>' % (
        safe_qualname(func), id(func))


@register_repr(type(sys))
def repr_module(module, _helper):
    return "<module '%s'>" % module.__name__


@register_repr(set)
def repr_set(x, helper):
    if not x:
        return repr(x)
    return helper.repr_iterable(x, '{', '}')


def sample_traceback():
    raw = u''.join(
        traceback.format_exception(*sys.exc_info())
    ).splitlines(True)
    tb = u''.join(
        line for line in raw
        if not line.strip().startswith("File")
        if not line.strip() == "raise value"  # part of six.reraise
    )
    sys.stderr.write(tb)


def assert_sample_output(module_name):
    module = import_module('tests.samples.' + module_name)
    old = sys.stderr

    out = io.StringIO()
    sys.stderr = out

    try:
        assert sys.gettrace() is None
        module.main()
        assert sys.gettrace() is None
    finally:
        sys.stderr = old

    time = '12:34:56.78'
    time_pattern = re.sub(r'\d', r'\\d', time)

    normalised = re.sub(time_pattern, time, out.getvalue()).strip()
    normalised = re.sub(r'0x\w+', '0xABC', normalised)
    normalised = normalised.replace('<genexpr>.<genexpr>', '<genexpr>')
    normalised = normalised.replace('<list_iterator', '<tupleiterator')
    normalised = normalised.replace('<listiterator', '<tupleiterator')
    normalised = normalised.replace('<tuple_iterator', '<tupleiterator')
    normalised = normalised.replace('<sequenceiterator', '<tupleiterator')
    normalised = normalised.replace(str(current_thread().ident), '123456789')

    result_filename = os.path.join(
        tests_dir,
        'sample_results',
        PYPY * 'pypy' + '.'.join(sys.version.split('.')[:2]),
        module_name + '.txt',
    )

    compare_to_file(normalised, result_filename)


def compare_to_file(text, filename):
    if os.environ.get('FIX_SNOOP_TESTS'):
        string_to_file(text, filename)
    else:
        expected_output = file_to_string(filename)
        assert text == expected_output


def generate_test_samples():
    samples_dir = os.path.join(tests_dir, 'samples')
    for filename in os.listdir(samples_dir):
        if filename.endswith('.pyc'):
            continue
        module_name = six.text_type(filename.split('.')[0])

        if module_name in '__init__ __pycache__':
            continue

        if module_name in 'django_sample'.split() and six.PY2:
            continue

        if PYPY or sys.version_info[:2] in ((3, 4), (3, 10)):
            if module_name in 'pandas_sample'.split():
                continue
        if NO_BIRDSEYE:
            if module_name in 'spy enabled'.split():
                continue

        if module_name in 'f_string' and sys.version_info[:2] < (3, 6):
            continue

        yield module_name


@pytest.mark.parametrize("module_name", generate_test_samples())
@pytest.mark.order(1)
def test_sample(module_name):
    assert_sample_output(module_name)


@pytest.mark.order(2)  # Execute after all test_samples have run.
def test_compare_versions():
    out = [""]

    def prn(*args):
        out[0] += " ".join(map(str, args)) + "\n"

    samples_dir = os.path.join(tests_dir, "samples")
    results_dir = os.path.join(tests_dir, "sample_results")
    versions = sorted(os.listdir(results_dir))
    for filename in sorted(os.listdir(samples_dir)):
        if not filename.endswith(".py"):
            continue
        module_name = filename[:-3]
        if module_name == "__init__":
            continue

        doesnt_exist = "Doesn't exist:"

        def get_results(version):
            path = os.path.join(results_dir, version, module_name + ".txt")
            if os.path.exists(path):
                return file_to_string(path)
            else:
                return doesnt_exist

        grouped = group_by_key_func(versions, get_results)

        if len(grouped) > 1:
            prn(module_name)
            doesnt_exist_versions = grouped.pop(doesnt_exist, None)
            if doesnt_exist_versions:
                prn(doesnt_exist, ", ".join(doesnt_exist_versions))
            if len(grouped) > 1:
                prn("Differing versions:")
                for version_group in sorted(grouped.values()):
                    prn(", ".join(version_group))
            prn()

    compare_to_file(out[0], os.path.join(tests_dir, "version_differences.txt"))


def test_string_io():
    string_io = io.StringIO()
    config = Config(out=string_io)
    contents = u'stuff'
    config.write(contents)
    assert string_io.getvalue() == contents


def test_callable():
    string_io = io.StringIO()

    def write(msg):
        string_io.write(msg)

    string_io = io.StringIO()
    config = Config(out=write)
    contents = u'stuff'
    config.write(contents)
    assert string_io.getvalue() == contents


def test_file_output():
    _, path = mkstemp()
    config = Config(out=path)
    contents = u'stuff'
    config.write(contents)
    with open(path) as output_file:
        output = output_file.read()
    assert output == contents


def test_no_overwrite_by_default():
    _, path = mkstemp()
    with open(path, 'w') as output_file:
        output_file.write(u'lala')
    config = Config(str(path))
    config.write(u' doo be doo')
    with open(path) as output_file:
        output = output_file.read()
    assert output == u'lala doo be doo'


def test_overwrite():
    _, path = mkstemp()
    with open(path, 'w') as output_file:
        output_file.write(u'lala')

    config = Config(out=str(path), overwrite=True)
    config.write(u'doo be')
    config.write(u' doo')

    with open(path) as output_file:
        output = output_file.read()
    assert output == u'doo be doo'


def test_needs_parentheses():
    assert not needs_parentheses('x')
    assert not needs_parentheses('x.y')
    assert not needs_parentheses('x.y.z')
    assert not needs_parentheses('x.y.z[0]')
    assert not needs_parentheses('x.y.z[0]()')
    assert not needs_parentheses('x.y.z[0]()(3, 4 * 5)')
    assert not needs_parentheses('foo(x)')
    assert not needs_parentheses('foo(x+y)')
    assert not needs_parentheses('(x+y)')
    assert not needs_parentheses('[x+1 for x in ()]')
    assert needs_parentheses('x + y')
    assert needs_parentheses('x * y')
    assert needs_parentheses('x and y')
    assert needs_parentheses('x if z else y')


def test_truncate_string():
    max_length = 20
    for i in range(max_length * 2):
        string = i * 'a'
        truncated = truncate_string(string, max_length)
        if len(string) <= max_length:
            assert string == truncated
        else:
            assert truncated == 'aaaaaaaa...aaaaaaaaa'
            assert len(truncated) == max_length


def test_truncate_list():
    max_length = 5
    for i in range(max_length * 2):
        lst = i * ['a']
        truncated = truncate_list(lst, max_length)
        if len(lst) <= max_length:
            assert lst == truncated
        else:
            assert truncated == ['a', 'a', '...', 'a', 'a']
            assert len(truncated) == max_length


class Foo(object):
    def bar1(self):
        pass

    @staticmethod
    def bar2():
        pass


def test_is_deep_arg():
    assert is_deep_arg(lambda: 0)
    assert not is_deep_arg(lambda x: 0)
    assert not is_deep_arg(lambda x=None: 0)
    assert not is_deep_arg(lambda *x: 0)
    assert not is_deep_arg(lambda **x: 0)
    assert not is_deep_arg(test_is_deep_arg)
    assert not is_deep_arg(Foo)
    assert not is_deep_arg(Foo.bar1)
    assert not is_deep_arg(Foo().bar1)
    assert not is_deep_arg(Foo.bar2)
    assert not is_deep_arg(Foo().bar2)


def test_no_asttokens_spy():
    if NO_ASTTOKENS:
        with pytest.raises(Exception, match="birdseye doesn't support this version of Python"):
            spy(test_is_deep_arg)
