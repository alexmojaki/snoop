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
Starting var:.. _one = 1
Starting var:.. _two = 2
Starting var:.. _three = 3
Starting var:.. _four = 4
12:34:56.789012 call         5 def f(_one, _two, _three, _four):
12:34:56.789012 line         6     _five = None
New var:....... _five = None
12:34:56.789012 line         7     _six = None
New var:....... _six = None
12:34:56.789012 line         8     _seven = None
New var:....... _seven = None
12:34:56.789012 line        10     _five, _six, _seven = 5, 6, 7
Modified var:.. _five = 5
Modified var:.. _six = 6
Modified var:.. _seven = 7
12:34:56.789012 return      10     _five, _six, _seven = 5, 6, 7
Return value:.. None
"""
