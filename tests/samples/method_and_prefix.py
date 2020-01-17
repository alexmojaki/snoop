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
