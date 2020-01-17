from __future__ import division


@snoop(depth=3)
def main():
    x = 1
    y = 2
    pp(pp(x + 1) + max(*pp(y + 2, y + 3)))
    assert pp.deep(lambda: x + 1 + max(y + 2, y + 3)) == 7
    lst = list(range(30))
    pp.deep(lambda: list(
        list(a + b for a in [1, 2])
        for b in [3, 4]
    ) + lst)
    pp(dict.fromkeys(range(30), 4))
    pp.deep(lambda: BadRepr() and 1)
    pp.deep(lambda: 1 / 2)

    try:
        pp.deep(lambda: max(y + 2, (y + 3) / 0))
    except ZeroDivisionError:
        pass
    else:
        assert 0

    f = pp.deep(lambda: caller(lambda: 2 * 3))
    f()


class BadRepr(object):
    def __repr__(self):
        raise ValueError('bad')


def caller(f):
    f()
    return f
