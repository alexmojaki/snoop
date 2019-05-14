from collections import OrderedDict

import pysnooper


class WithSlots(object):
    __slots__ = ('x', 'y')

    def __init__(self):
        self.x = 3
        self.y = 4


@pysnooper.snoop(watch=(
        pysnooper.Keys('_d', exclude='c'),
        pysnooper.Attrs('_s'),
        pysnooper.Indices('_lst')[-3:],
        pysnooper.Attrs('_lst'),  # doesn't have attributes
))
def main():
    _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
    _s = WithSlots()
    _lst = list(range(1000))


expected_output = """
12:34:56.78 call        20 def main():
12:34:56.78 line        21     _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
........... _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
........... _d['a'] = 1
........... _d['b'] = 2
12:34:56.78 line        22     _s = WithSlots()
........... _s = <tests.samples.variables_cla...hSlots object at 0xABC>
........... _s.x = 3
........... _s.y = 4
12:34:56.78 line        23     _lst = list(range(1000))
........... _lst = [0, 1, 2, ..., 997, 998, 999]
........... _lst[997] = 997
........... _lst[998] = 998
........... _lst[999] = 999
<<< Return value from main: None
"""
