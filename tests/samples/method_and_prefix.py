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
ZZZ............... self = <tests.samples.method_and_prefix.Baz object at 0xABC>
ZZZ............... self.x = 2
ZZZ12:34:56.789012 call         9     def square(self):
ZZZ12:34:56.789012 line        10         foo = 7
ZZZ............... foo = 7
ZZZ12:34:56.789012 line        11         self.x **= 2
ZZZ............... self.x = 4
ZZZ12:34:56.789012 line        12         return self
ZZZ12:34:56.789012 return      12         return self
ZZZReturn value:.. <tests.samples.method_and_prefix.Baz object at 0xABC>
"""
