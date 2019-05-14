import pysnooper


def f4(x4):
    result4 = x4 * 2
    return result4


def f3(x3):
    result3 = f4(x3)
    return result3


def f2(x2):
    result2 = f3(x2)
    return result2


@pysnooper.snoop(depth=3)
def main():
    result1 = f2(8)
    return result1


expected_output = """
12:34:56.78 call        20 def main():
12:34:56.78 line        21     result1 = f2(8)
    ........... x2 = 8
    12:34:56.78 call        14 def f2(x2):
    12:34:56.78 line        15     result2 = f3(x2)
        ........... x3 = 8
        12:34:56.78 call         9 def f3(x3):
        12:34:56.78 line        10     result3 = f4(x3)
        ........... result3 = 16
        12:34:56.78 line        11     return result3
        <<< Return value from f3: 16
    ........... result2 = 16
    12:34:56.78 line        16     return result2
    <<< Return value from f2: 16
........... result1 = 16
12:34:56.78 line        22     return result1
<<< Return value from main: 16
"""
