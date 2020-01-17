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
