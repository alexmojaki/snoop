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
12:34:56.789012 call        20 def main():
12:34:56.789012 line        21     _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
New var:....... _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
New var:....... _d['a'] = 1
New var:....... _d['b'] = 2
12:34:56.789012 line        22     _s = WithSlots()
New var:....... _s = <tests.samples.variables_cla...hSlots object at 0xABC>
New var:....... _s.x = 3
New var:....... _s.y = 4
12:34:56.789012 line        23     _lst = list(range(1000))
New var:....... _lst = [0, 1, 2, ..., 997, 998, 999]
New var:....... _lst[997] = 997
New var:....... _lst[998] = 998
New var:....... _lst[999] = 999
12:34:56.789012 return      23     _lst = list(range(1000))
Return value:.. None
"""
