# Copyright 2019 Ram Rachum and collaborators.
# This program is distributed under the MIT license.

import io
import os
import re
from importlib import import_module

import pytest
import six
from python_toolbox import sys_tools, temp_file_tools
from littleutils import file_to_string, string_to_file
from cheap_repr import cheap_repr, register_repr
from cheap_repr.utils import safe_qualname

import pysnooper
from pysnooper.utils import truncate_string, truncate_list
from pysnooper.variables import needs_parentheses


@register_repr(type(cheap_repr))
def repr_function(func, _helper):
    return '<function %s at %#x>' % (
        safe_qualname(func), id(func))


def assert_sample_output(module):
    with sys_tools.OutputCapturer(stdout=False,
                                  stderr=True) as output_capturer:
        module.main()

    time = '12:34:56.78'
    time_pattern = re.sub(r'\d', r'\\d', time)

    output = output_capturer.string_io.getvalue()

    normalised = re.sub(time_pattern, time, output).strip()
    normalised = re.sub(r'at 0x\w+>', 'at 0xABC>', normalised)

    try:
        assert (
                normalised ==
                module.expected_output.strip()
        )
    except AssertionError:
        fix = 1
        if fix:
            path = module.__file__.rstrip('c')
            contents = file_to_string(path)
            match = re.search(
                r'expected_output = """',
                contents,
            )
            contents = contents[:match.end(0)] + '\n{}\n"""\n'.format(normalised)
            string_to_file(contents, path)
        else:
            print('\n\nNormalised actual output:\n\n' + normalised)
            raise  # show pytest diff (may need -vv flag to see in full)


def test_samples():
    samples_dir = os.path.join(os.path.dirname(__file__), 'samples')
    for filename in os.listdir(samples_dir):
        module_name = six.text_type(filename.split('.')[0])
        if module_name in '__init__ __pycache__':
            continue
        module = import_module('tests.samples.' + module_name)
        assert_sample_output(module)


def test_string_io():
    string_io = io.StringIO()
    tracer = pysnooper.snoop(string_io)
    contents = u'stuff'
    tracer._write(contents)
    assert string_io.getvalue() == contents


def test_callable():
    string_io = io.StringIO()

    def write(msg):
        string_io.write(msg)

    string_io = io.StringIO()
    tracer = pysnooper.snoop(write)
    contents = u'stuff'
    tracer._write(contents)
    assert string_io.getvalue() == contents


def test_file_output():
    with temp_file_tools.create_temp_folder(prefix='pysnooper') as folder:
        path = folder / 'foo.log'

        tracer = pysnooper.snoop(path)
        contents = u'stuff'
        tracer._write(contents)
        with path.open() as output_file:
            output = output_file.read()
        assert output == contents


def test_no_overwrite_by_default():
    with temp_file_tools.create_temp_folder(prefix='pysnooper') as folder:
        path = folder / 'foo.log'
        with path.open('w') as output_file:
            output_file.write(u'lala')
        tracer = pysnooper.snoop(str(path))
        tracer._write(u' doo be doo')
        with path.open() as output_file:
            output = output_file.read()
        assert output == u'lala doo be doo'


def test_overwrite():
    with temp_file_tools.create_temp_folder(prefix='pysnooper') as folder:
        path = folder / 'foo.log'
        with path.open('w') as output_file:
            output_file.write(u'lala')

        tracer = pysnooper.snoop(str(path), overwrite=True)
        tracer._write(u'doo be')
        tracer._write(u' doo')

        with path.open() as output_file:
            output = output_file.read()
        assert output == u'doo be doo'


def test_error_in_overwrite_argument():
    with temp_file_tools.create_temp_folder(prefix='pysnooper'):
        with pytest.raises(Exception, match='can only be used when writing'):
            @pysnooper.snoop(overwrite=True)
            def my_function():
                x = 7
                y = 8
                return y + x


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
