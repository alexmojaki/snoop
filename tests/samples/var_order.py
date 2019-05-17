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
12:34:56.78 >>> Call to f in var_order.py
12:34:56.78 ...... _one = 1
12:34:56.78 ...... _two = 2
12:34:56.78 ...... _three = 3
12:34:56.78 ...... _four = 4
12:34:56.78    5 | def f(_one, _two, _three, _four):
12:34:56.78    6 |     _five = None
12:34:56.78    7 |     _six = None
12:34:56.78    8 |     _seven = None
12:34:56.78   10 |     _five, _six, _seven = 5, 6, 7
12:34:56.78 .......... _five = 5
12:34:56.78 .......... _six = 6
12:34:56.78 .......... _seven = 7
12:34:56.78 <<< Return value from f: None
"""
