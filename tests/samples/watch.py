import pysnooper


class Foo(object):
    def __init__(self):
        self.x = 2

    def square(self):
        self.x **= 2


@pysnooper.snoop(watch=(
        'foo.x',
        'io.__name__',
        'len(foo.__dict__["x"] * "abc")',
))
def main():
    foo = Foo()
    for i in range(2):
        foo.square()


expected_output = """
12:34:56.789012 call        17 def main():
12:34:56.789012 line        18     foo = Foo()
New var:....... foo = <tests.samples.watch.Foo object at 0xABC>
New var:....... foo.x = 2
New var:....... len(foo.__dict__["x"] * "abc") = 6
12:34:56.789012 line        19     for i in range(2):
New var:....... i = 0
12:34:56.789012 line        20         foo.square()
Modified var:.. foo.x = 4
Modified var:.. len(foo.__dict__["x"] * "abc") = 12
12:34:56.789012 line        19     for i in range(2):
Modified var:.. i = 1
12:34:56.789012 line        20         foo.square()
Modified var:.. foo.x = 16
Modified var:.. len(foo.__dict__["x"] * "abc") = 48
12:34:56.789012 line        19     for i in range(2):
12:34:56.789012 return      19     for i in range(2):
Return value:.. None
"""
