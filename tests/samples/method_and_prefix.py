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
ZZZ12:34:56.78 >>> Call to square in method_and_prefix.py
ZZZ12:34:56.78 ...... self = <tests.samples.method_and_prefix.Baz object at 0xABC>
ZZZ12:34:56.78 ...... self.x = 2
ZZZ12:34:56.78    9 |     def square(self):
ZZZ12:34:56.78   10 |         foo = 7
ZZZ12:34:56.78 ...... foo = 7
ZZZ12:34:56.78   11 |         self.x **= 2
ZZZ12:34:56.78 ...... self.x = 4
ZZZ12:34:56.78   12 |         return self
ZZZ12:34:56.78 <<< Return value from square: <tests.samples.method_and_prefix.Baz object at 0xABC>
"""
