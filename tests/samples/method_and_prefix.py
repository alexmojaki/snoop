from snoop.configuration import Config

snoop = Config(prefix='ZZZ').snoop


class Baz(object):
    def __init__(self):
        self.x = 2

    @snoop(watch='self.x')
    def square(self):
        foo = 7
        self.x **= 2
        return self


def main():
    baz = Baz()
    baz.square()


expected_output = """
ZZZ 12:34:56.78 >>> Call to square in File "/path/to_file.py", line 11
ZZZ 12:34:56.78 .......... self = <tests.samples.method_and_prefix.Baz object at 0xABC>
ZZZ 12:34:56.78 .......... self.x = 2
ZZZ 12:34:56.78   11 |     def square(self):
ZZZ 12:34:56.78   12 |         foo = 7
ZZZ 12:34:56.78   13 |         self.x **= 2
ZZZ 12:34:56.78 .............. self.x = 4
ZZZ 12:34:56.78   14 |         return self
ZZZ 12:34:56.78 <<< Return value from square: <tests.samples.method_and_prefix.Baz object at 0xABC>
"""
