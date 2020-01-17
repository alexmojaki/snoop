import snoop


class Foo(object):
    def __init__(self):
        self.x = 2

    def square(self):
        self.x **= 2


@snoop.snoop(watch=(
        'foo.x',
        'io.__name__',
        'len(foo.__dict__["x"] * "abc")',
))
def main():
    foo = Foo()
    for i in range(2):
        foo.square()
