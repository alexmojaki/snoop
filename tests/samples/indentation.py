import snoop


@snoop.snoop(depth=2)
def main():
    f2()


def f2():
    f3()


def f3():
    f4()


@snoop.snoop(depth=2)
def f4():
    f5()


def f5():
    pass


if __name__ == '__main__':
    main()
