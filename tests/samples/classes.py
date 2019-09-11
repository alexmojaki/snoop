@snoop
class Foo(object):
    def bar(self):
        return 5

    @snoop(watch='self.x')
    def spam(self):
        return 8

    @property
    def prop(self):
        return self.bar()

    @staticmethod
    def state():
        return 0


def main():
    foo = Foo()
    foo.x = 3
    assert foo.spam() == 8
    assert foo.prop == 5
    assert Foo.state() == 0


expected_output = """
12:34:56.78 >>> Call to Foo.spam in File "/path/to_file.py", line 7
12:34:56.78 .......... self = <tests.samples.classes.Foo object at 0xABC>
12:34:56.78 .......... self.x = 3
12:34:56.78    7 |     def spam(self):
12:34:56.78    8 |         return 8
12:34:56.78 <<< Return value from Foo.spam: 8
12:34:56.78 >>> Call to Foo.prop in File "/path/to_file.py", line 11
12:34:56.78 .......... self = <tests.samples.classes.Foo object at 0xABC>
12:34:56.78   11 |     def prop(self):
12:34:56.78   12 |         return self.bar()
    12:34:56.78 >>> Call to Foo.bar in File "/path/to_file.py", line 3
    12:34:56.78 .......... self = <tests.samples.classes.Foo object at 0xABC>
    12:34:56.78    3 |     def bar(self):
    12:34:56.78    4 |         return 5
    12:34:56.78 <<< Return value from Foo.bar: 5
12:34:56.78   12 |         return self.bar()
12:34:56.78 <<< Return value from Foo.prop: 5
12:34:56.78 >>> Call to Foo.state in File "/path/to_file.py", line 15
12:34:56.78   15 |     def state():
12:34:56.78   16 |         return 0
12:34:56.78 <<< Return value from Foo.state: 0
"""
