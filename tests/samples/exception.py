import pysnooper


def foo():
    raise TypeError('bad')


def bar():
    try:
        foo()
    except Exception:
        str(1)
        raise


@pysnooper.snoop(depth=3)
def main():
    try:
        bar()
    except:
        pass


expected_output = """
12:34:56.78 >>> Call to main in exception.py
12:34:56.78   17 | def main():
12:34:56.78   18 |     try:
12:34:56.78   19 |         bar()
    12:34:56.78 >>> Call to bar in exception.py
    12:34:56.78    8 | def bar():
    12:34:56.78    9 |     try:
    12:34:56.78   10 |         foo()
        12:34:56.78 >>> Call to foo in exception.py
        12:34:56.78    4 | def foo():
        12:34:56.78    5 |     raise TypeError('bad')
        12:34:56.78 !!! TypeError: bad
        12:34:56.78 !!! Call ended by exception
    12:34:56.78   10 |         foo()
    12:34:56.78 !!! TypeError: bad
    12:34:56.78   11 |     except Exception:
    12:34:56.78   12 |         str(1)
    12:34:56.78   13 |         raise
    12:34:56.78 !!! Call ended by exception
12:34:56.78   19 |         bar()
12:34:56.78 !!! TypeError: bad
12:34:56.78   20 |     except:
12:34:56.78   21 |         pass
12:34:56.78 <<< Return value from main: None
"""
