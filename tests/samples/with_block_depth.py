import snoop


def f4(x4):
    result4 = x4 * 2
    return result4


def f3(x3):
    result3 = f4(x3)
    return result3


def f2(x2):
    result2 = f3(x2)
    return result2


def main():
    str(3)
    with snoop.snoop(depth=3):
        result1 = f2(5)
    return result1
