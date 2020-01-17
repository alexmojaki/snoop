import snoop


def f4(x4):
    result4 = snoop.pp(x4 * 2)
    return result4


def f3(x3):
    result3 = f4(x3)
    return result3


def f2(x2):
    result2 = f3(x2)
    return result2


@snoop(depth=3)
def main():
    result1 = f2(8)
    return result1


if __name__ == '__main__':
    main()
