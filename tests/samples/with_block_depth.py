import snoop


def f4(x4):
    return x4 * 2


def f3(x3):
    return f4(x3)


def f2(x2):
    return f3(x2)


def main():
    str(3)
    with snoop.snoop(depth=3):
        result1 = f2(5)
    return result1
