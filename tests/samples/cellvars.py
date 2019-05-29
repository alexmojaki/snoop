import pysnooper


def f2(a):
    def f3(a):
        x = 0
        x += 1

        def f4(_a):
            _y = x
            return 42

        return f4(a)

    return f3(a)


def main():
    with pysnooper.snoop(depth=4):
        result1 = f2(42)
    return result1


expected_output = """
12:34:56.78 >>> Enter with block in main in cellvars.py
12:34:56.78   20 |         result1 = f2(42)
    12:34:56.78 >>> Call to f2 in cellvars.py
    12:34:56.78 ...... a = 42
    12:34:56.78    4 | def f2(a):
    12:34:56.78    5 |     def f3(a):
    12:34:56.78   15 |     return f3(a)
        12:34:56.78 >>> Call to f3 in cellvars.py
        12:34:56.78 .......... a = 42
        12:34:56.78    5 |     def f3(a):
        12:34:56.78    6 |         x = 0
        12:34:56.78    7 |         x += 1
        12:34:56.78 .............. x = 1
        12:34:56.78    9 |         def f4(_a):
        12:34:56.78   13 |         return f4(a)
            12:34:56.78 >>> Call to f4 in cellvars.py
            12:34:56.78 .............. _a = 42
            12:34:56.78 .............. x = 1
            12:34:56.78    9 |         def f4(_a):
            12:34:56.78   10 |             _y = x
            12:34:56.78 .................. _y = 1
            12:34:56.78   11 |             return 42
            12:34:56.78 <<< Return value from f4: 42
        12:34:56.78   13 |         return f4(a)
        12:34:56.78 <<< Return value from f3: 42
    12:34:56.78   15 |     return f3(a)
    12:34:56.78 <<< Return value from f2: 42
12:34:56.78   20 |         result1 = f2(42)
12:34:56.78 .............. result1 = 42
12:34:56.78 <<< Exit with block in main
"""
