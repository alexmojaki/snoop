from snoop.configuration import Config


def watch_type(source, value):
    return 'type({})'.format(source), type(value).__name__


def foo():
    x = 1
    y = [x]
    return y


def main():
    Config(watch_extras=watch_type).snoop(foo)()
    Config(replace_watch_extras=watch_type).snoop(foo)()


expected_output = """
12:34:56.78 >>> Call to foo in File "/path/to_file.py", line 8
12:34:56.78    8 | def foo():
12:34:56.78    9 |     x = 1
12:34:56.78 .......... type(x) = 'int'
12:34:56.78   10 |     y = [x]
12:34:56.78 .......... y = [1]
12:34:56.78 .......... len(y) = 1
12:34:56.78 .......... type(y) = 'list'
12:34:56.78   11 |     return y
12:34:56.78 <<< Return value from foo: [1]
12:34:56.78 >>> Call to foo in File "/path/to_file.py", line 8
12:34:56.78    8 | def foo():
12:34:56.78    9 |     x = 1
12:34:56.78 .......... type(x) = 'int'
12:34:56.78   10 |     y = [x]
12:34:56.78 .......... y = [1]
12:34:56.78 .......... type(y) = 'list'
12:34:56.78   11 |     return y
12:34:56.78 <<< Return value from foo: [1]
"""
