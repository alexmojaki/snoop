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
12:34:56.78 >>> Call to main in indentation.py
12:34:56.78    5 | def main():
12:34:56.78    6 |     f2()
    12:34:56.78 >>> Call to f2 in indentation.py
    12:34:56.78    9 | def f2():
    12:34:56.78   10 |     f3()
        12:34:56.78 >>> Call to f4 in indentation.py
        12:34:56.78   18 | def f4():
        12:34:56.78   19 |     f5()
            12:34:56.78 >>> Call to f5 in indentation.py
            12:34:56.78   22 | def f5():
            12:34:56.78   23 |     pass
            12:34:56.78 <<< Return value from f5: None
        12:34:56.78   19 |     f5()
        12:34:56.78 <<< Return value from f4: None
    12:34:56.78 <<< Return value from f2: None
12:34:56.78    6 |     f2()
12:34:56.78 <<< Return value from main: None
"""
