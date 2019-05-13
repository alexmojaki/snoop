import pysnooper


@pysnooper.snoop(depth=2)
def factorial(x):
    if x <= 1:
        return 1
    return mul(x, factorial(x - 1))


def mul(a, b):
    return a * b


def main():
    factorial(4)
    
expected_output = """
Starting var:.. x = 4
12:34:56.789012 call         5 def factorial(x):
12:34:56.789012 line         6     if x <= 1:
12:34:56.789012 line         8     return mul(x, factorial(x - 1))
    Starting var:.. x = 3
    12:34:56.789012 call         5 def factorial(x):
    12:34:56.789012 line         6     if x <= 1:
    12:34:56.789012 line         8     return mul(x, factorial(x - 1))
        Starting var:.. x = 2
        12:34:56.789012 call         5 def factorial(x):
        12:34:56.789012 line         6     if x <= 1:
        12:34:56.789012 line         8     return mul(x, factorial(x - 1))
            Starting var:.. x = 1
            12:34:56.789012 call         5 def factorial(x):
            12:34:56.789012 line         6     if x <= 1:
            12:34:56.789012 line         7         return 1
            12:34:56.789012 return       7         return 1
            Return value:.. 1
            Starting var:.. a = 2
            Starting var:.. b = 1
            12:34:56.789012 call        11 def mul(a, b):
            12:34:56.789012 line        12     return a * b
            12:34:56.789012 return      12     return a * b
            Return value:.. 2
        12:34:56.789012 return       8     return mul(x, factorial(x - 1))
        Return value:.. 2
        Starting var:.. a = 3
        Starting var:.. b = 2
        12:34:56.789012 call        11 def mul(a, b):
        12:34:56.789012 line        12     return a * b
        12:34:56.789012 return      12     return a * b
        Return value:.. 6
    12:34:56.789012 return       8     return mul(x, factorial(x - 1))
    Return value:.. 6
    Starting var:.. a = 4
    Starting var:.. b = 6
    12:34:56.789012 call        11 def mul(a, b):
    12:34:56.789012 line        12     return a * b
    12:34:56.789012 return      12     return a * b
    Return value:.. 24
12:34:56.789012 return       8     return mul(x, factorial(x - 1))
Return value:.. 24
"""
