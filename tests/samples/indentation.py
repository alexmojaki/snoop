import pysnooper


@pysnooper.snoop(depth=2)
def main():
    f2()


def f2():
    f3()


def f3():
    f4()


@pysnooper.snoop(depth=2)
def f4():
    f5()


def f5():
    pass


expected_output = """
12:34:56.78 call         5 def main():
12:34:56.78 line         6     f2()
    12:34:56.78 call         9 def f2():
    12:34:56.78 line        10     f3()
        12:34:56.78 call        18 def f4():
        12:34:56.78 line        19     f5()
            12:34:56.78 call        22 def f5():
            12:34:56.78 line        23     pass
            12:34:56.78 return      23     pass
            Return value: None
        12:34:56.78 return      19     f5()
        Return value: None
    12:34:56.78 return      10     f3()
    Return value: None
12:34:56.78 return       6     f2()
Return value: None
"""
