import pysnooper


class Baz(object):
    def __init__(self):
        self.x = 2

    @pysnooper.snoop(watch=('self.x',), prefix='ZZZ')
    def square(self):
        foo = 7
        self.x **= 2
        return self


def main():
    baz = Baz()
    baz.square()


expected_output = """
ZZZ 12:34:56.78 >>> Call to square in method_and_prefix.py
ZZZ 12:34:56.78 .......... self = <tests.samples.method_and_prefix.Baz object at 0xABC>
ZZZ 12:34:56.78 .......... self.x = 2
ZZZ 12:34:56.78    9 |     def square(self):
ZZZ 12:34:56.78   10 |         foo = 7
ZZZ 12:34:56.78   11 |         self.x **= 2
ZZZ 12:34:56.78 .............. self.x = 4
ZZZ 12:34:56.78   12 |         return self
ZZZ 12:34:56.78 <<< Return value from square: <tests.samples.method_and_prefix.Baz object at 0xABC>
"""
