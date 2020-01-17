import snoop


@snoop
def foo(e):
    try:
        if e:
            raise TypeError('bad')
        return
    finally:
        pass


def main():
    foo(0)
    try:
        foo(1)
    except TypeError:
        pass


if __name__ == '__main__':
    main()
