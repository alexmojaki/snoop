from collections import OrderedDict

import snoop


class Foo(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


@snoop.snoop(watch_explode=('_d', '_point', 'lst + []'))
def main():
    _d = OrderedDict([('a', 1), ('b', 2), ('c', 'ignore')])
    _point = Foo(x=3, y=4)
    lst = [7, 8, 9]
    lst.append(10)
