import snoop


@snoop.snoop()
def f(_one, _two, _three, _four):
    _five = None
    _six = None
    _seven = None

    _five, _six, _seven = 5, 6, 7


def main():
    f(1, 2, 3, 4)
