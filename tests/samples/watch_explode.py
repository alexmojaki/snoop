from collections import OrderedDict

import pysnooper


class Foo(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


@pysnooper.snoop(watch_explode=('_d', '_point', 'lst + []'))
def main():
    _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
    _point = Foo(x=3, y=4)
    lst = [7, 8, 9]
    lst.append(10)

expected_output = """
12:34:56.78 call        13 def main():
12:34:56.78 line        14     _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
........... _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
........... _d['a'] = 1
........... _d['b'] = 2
........... _d['c'] = 'ignore'
12:34:56.78 line        15     _point = Foo(x=3, y=4)
........... _point = <tests.samples.watch_explode.Foo object at 0xABC>
........... _point.x = 3
........... _point.y = 4
12:34:56.78 line        16     lst = [7, 8, 9]
........... lst = [7, 8, 9]
........... (lst + [])[0] = 7
........... (lst + [])[1] = 8
........... (lst + [])[2] = 9
........... lst + [] = [7, 8, 9]
12:34:56.78 line        17     lst.append(10)
........... lst = [7, 8, 9, 10]
........... (lst + [])[3] = 10
........... lst + [] = [7, 8, 9, 10]
Return value: None
"""
