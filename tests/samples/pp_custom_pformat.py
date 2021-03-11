
def test():
    x = 10
    y = 20
    assert pp(pp(x + y) + y) == 50
    assert pp.deep(lambda: (x + y) + y) == 50
    pp([14, 15, 16])

    with snoop:
        z = 30  # custom pformat is not used here

def main():
    snoop.install(pformat=lambda x: 'custom(' + repr(x) + ')')
    test()

    snoop.install(pformat=None)
    test()
