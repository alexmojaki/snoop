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
12:34:56.789012 call        20 def main():
12:34:56.789012 line        21     result1 = f2(8)
    Starting var:.. x2 = 8
    12:34:56.789012 call        14 def f2(x2):
    12:34:56.789012 line        15     result2 = f3(x2)
        Starting var:.. x3 = 8
        12:34:56.789012 call         9 def f3(x3):
        12:34:56.789012 line        10     result3 = f4(x3)
        New var:....... result3 = 16
        12:34:56.789012 line        11     return result3
        12:34:56.789012 return      11     return result3
        Return value:.. 16
    New var:....... result2 = 16
    12:34:56.789012 line        16     return result2
    12:34:56.789012 return      16     return result2
    Return value:.. 16
New var:....... result1 = 16
12:34:56.789012 line        22     return result1
12:34:56.789012 return      22     return result1
Return value:.. 16
"""
