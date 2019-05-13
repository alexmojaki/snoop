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
12:34:56.789012 call        13 def main():
12:34:56.789012 line        14     _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
New var:....... _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
New var:....... _d['a'] = 1
New var:....... _d['b'] = 2
New var:....... _d['c'] = 'ignore'
12:34:56.789012 line        15     _point = Foo(x=3, y=4)
New var:....... _point = <tests.samples.watch_explode.Foo object at 0xABC>
New var:....... _point.x = 3
New var:....... _point.y = 4
12:34:56.789012 line        16     lst = [7, 8, 9]
New var:....... lst = [7, 8, 9]
New var:....... (lst + [])[0] = 7
New var:....... (lst + [])[1] = 8
New var:....... (lst + [])[2] = 9
New var:....... lst + [] = [7, 8, 9]
12:34:56.789012 line        17     lst.append(10)
Modified var:.. lst = [7, 8, 9, 10]
New var:....... (lst + [])[3] = 10
Modified var:.. lst + [] = [7, 8, 9, 10]
12:34:56.789012 return      17     lst.append(10)
Return value:.. None
"""
