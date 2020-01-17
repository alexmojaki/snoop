from collections import OrderedDict

import snoop


class WithSlots(object):
    __slots__ = ('x', 'y')

    def __init__(self):
        self.x = 3
        self.y = 4


@snoop.snoop(watch=(
        snoop.Keys('_d', exclude='c'),
        snoop.Attrs('_s'),
        snoop.Indices('_lst')[-3:],
        snoop.Attrs('_lst'),  # doesn't have attributes
))
def main():
    _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
    _s = WithSlots()
    _lst = list(range(1000))
