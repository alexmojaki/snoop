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
12:34:56.78 >>> Call to main in variables_classes.py
12:34:56.78   20 | def main():
12:34:56.78   21 |     _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
12:34:56.78 .......... _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
12:34:56.78 .......... _d['a'] = 1
12:34:56.78 .......... _d['b'] = 2
12:34:56.78   22 |     _s = WithSlots()
12:34:56.78 .......... _s = <tests.samples.variables_cla...hSlots object at 0xABC>
12:34:56.78 .......... _s.x = 3
12:34:56.78 .......... _s.y = 4
12:34:56.78   23 |     _lst = list(range(1000))
12:34:56.78 .......... _lst = [0, 1, 2, ..., 997, 998, 999]
12:34:56.78 .......... _lst[997] = 997
12:34:56.78 .......... _lst[998] = 998
12:34:56.78 .......... _lst[999] = 999
12:34:56.78 <<< Return value from main: None
"""
