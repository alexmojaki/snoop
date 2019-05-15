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
12:34:56.78 >>> Call to main in watch_explode.py
12:34:56.78   13 | def main():
12:34:56.78   14 |     _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
12:34:56.78 ...... _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
12:34:56.78 ...... _d['a'] = 1
12:34:56.78 ...... _d['b'] = 2
12:34:56.78 ...... _d['c'] = 'ignore'
12:34:56.78   15 |     _point = Foo(x=3, y=4)
12:34:56.78 ...... _point = <tests.samples.watch_explode.Foo object at 0xABC>
12:34:56.78 ...... _point.x = 3
12:34:56.78 ...... _point.y = 4
12:34:56.78   16 |     lst = [7, 8, 9]
12:34:56.78 ...... lst = [7, 8, 9]
12:34:56.78 ...... (lst + [])[0] = 7
12:34:56.78 ...... (lst + [])[1] = 8
12:34:56.78 ...... (lst + [])[2] = 9
12:34:56.78 ...... lst + [] = [7, 8, 9]
12:34:56.78   17 |     lst.append(10)
12:34:56.78 ...... lst = [7, 8, 9, 10]
12:34:56.78 ...... (lst + [])[3] = 10
12:34:56.78 ...... lst + [] = [7, 8, 9, 10]
12:34:56.78 <<< Return value from main: None
"""
