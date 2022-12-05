import snoop


def foo():
    raise TypeError('''
    very
    bad''')


def bar(*_):
    try:
        str(foo())
    except Exception:
        str(1)
        raise


@snoop(depth=3)
def main():
    try:
        bar()
    except:
        pass

    try:
        bob(
            1,
            2
        )
    except:
        pass

    try:
        (None
         or bob)(
            1,
            2
        )
    except:
        pass

    x = [[[2]]]

    try:
        str(x[1][0][0])
    except:
        pass

    try:
        str(x[0][1][0])
    except:
        pass

    try:
        str(x[0][0][1])
    except:
        pass


def bob(*_):
    pass


bob()
bob = None


if __name__ == '__main__':
    main()
