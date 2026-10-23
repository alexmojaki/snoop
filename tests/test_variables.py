import pytest

from snoop.variables import Attrs


@pytest.mark.parametrize('slots', ['value', ('value',), ['value']])
def test_attrs_single_slot(slots):
    class Example:
        __slots__ = slots

    value = Example()
    value.value = 42

    assert Attrs('obj')._items(value) == [('obj', value), ('obj.value', 42)]
    assert Attrs('obj', exclude='value')._items(value) == [('obj', value)]
