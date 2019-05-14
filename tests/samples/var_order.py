import pysnooper


@pysnooper.snoop()
def f(_one, _two, _three, _four):
    _five = None
    _six = None
    _seven = None

    _five, _six, _seven = 5, 6, 7


def main():
    f(1, 2, 3, 4)


expected_output = """
........... _one = 1
........... _two = 2
........... _three = 3
........... _four = 4
12:34:56.78 call         5 def f(_one, _two, _three, _four):
12:34:56.78 line         6     _five = None
........... _five = None
12:34:56.78 line         7     _six = None
........... _six = None
12:34:56.78 line         8     _seven = None
........... _seven = None
12:34:56.78 line        10     _five, _six, _seven = 5, 6, 7
........... _five = 5
........... _six = 6
........... _seven = 7
<<< Return value from f: None
"""
