import sys

import pytest

import pysnooper

original_tracer = sys.gettrace()
original_tracer_active = lambda: (sys.gettrace() is original_tracer)


@pysnooper.snoop()
def f(x1):
    assert not original_tracer_active()
    _x2 = (yield x1)
    assert not original_tracer_active()
    _x3 = 'foo'
    assert not original_tracer_active()
    _x4 = (yield 2)
    assert not original_tracer_active()
    return


def main():
    assert original_tracer_active()
    generator = f(0)
    assert original_tracer_active()
    first_item = next(generator)
    assert original_tracer_active()
    assert first_item == 0
    second_item = generator.send('blabla')
    assert original_tracer_active()
    assert second_item == 2
    with pytest.raises(StopIteration):
        generator.send('looloo')
    assert original_tracer_active()


expected_output = """
12:34:56.78 >>> Call to f in generator.py
12:34:56.78 ...... x1 = 0
12:34:56.78   12 | def f(x1):
12:34:56.78   13 |     assert not original_tracer_active()
12:34:56.78   14 |     _x2 = (yield x1)
12:34:56.78 <<< Return value from f: 0
12:34:56.78 >>> Call to f in generator.py
12:34:56.78 .......... x1 = 0
12:34:56.78   14 |     _x2 = (yield x1)
12:34:56.78 .......... _x2 = 'blabla'
12:34:56.78   15 |     assert not original_tracer_active()
12:34:56.78   16 |     _x3 = 'foo'
12:34:56.78   17 |     assert not original_tracer_active()
12:34:56.78   18 |     _x4 = (yield 2)
12:34:56.78 <<< Return value from f: 2
12:34:56.78 >>> Call to f in generator.py
12:34:56.78 .......... x1 = 0
12:34:56.78 .......... _x2 = 'blabla'
12:34:56.78 .......... _x3 = 'foo'
12:34:56.78   18 |     _x4 = (yield 2)
12:34:56.78 .......... _x4 = 'looloo'
12:34:56.78   19 |     assert not original_tracer_active()
12:34:56.78   20 |     return
12:34:56.78 <<< Return value from f: None
"""
