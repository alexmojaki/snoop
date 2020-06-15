import snoop


def f4(x4):
    return snoop.pp(x4 * 2)


def f3(x3):
    return f4(x3)


def f2(x2):
    return f3(x2)


@snoop(depth=3)
def main():
    return f2(8)


if __name__ == '__main__':
    main()
