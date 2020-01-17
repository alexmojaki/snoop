import sys

import pytest

import snoop

original_tracer = sys.gettrace()
original_tracer_active = lambda: (sys.gettrace() is original_tracer)


@snoop.snoop()
def f(x1):
    assert not original_tracer_active()
    _x2 = (yield x1)
    assert not original_tracer_active()
    _x3 = 'foo'
    assert not original_tracer_active()
    _x4 = (yield 2)
    assert not original_tracer_active()


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


if __name__ == '__main__':
    main()
