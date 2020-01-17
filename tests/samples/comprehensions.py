@snoop()
def foo(x):
    return x ** 2


def no_trace(_x):
    return 3


@snoop(depth=2)
def bar():
    str({no_trace(x) for x in (1, 2)})


@snoop()
def main():
    str({x for x in list(range(100))})
    str({x: x for x in list(range(100))})
    str({y: {x + y for x in list(range(3))} for y in list(range(3))})
    str({foo(x) for x in (1, 2)})
    str({no_trace(x) for x in (1, 2)})
    bar()
