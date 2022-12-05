import snoop

# Testing that a single Tracer can handle many mixed uses
snoop = snoop()


def foo(x):
    if x == 0:
        bar1(x)
        qux()
        return

    with snoop:
        # There should be line entries for these three lines,
        # no line entries for anything else in this function,
        # but calls to all bar functions should be traced
        foo(x - 1)
        bar2(x)
        qux()
    int(4)
    bar3(9)
    return x


@snoop
def bar1(_x):
    qux()


@snoop
def bar2(_x):
    qux()


@snoop
def bar3(_x):
    qux()


def qux():
    return 9  # not traced, mustn't show up


def gen():
    for i in [1, 2]:
        if i == 1:
            with snoop:
                yield i


def main():
    foo(2)
    list(gen())


if __name__ == '__main__':
    main()
