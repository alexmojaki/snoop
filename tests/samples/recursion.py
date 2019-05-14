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
........... x = 4
12:34:56.78 call         5 def factorial(x):
12:34:56.78 line         6     if x <= 1:
12:34:56.78 line         8     return mul(x, factorial(x - 1))
    ........... x = 3
    12:34:56.78 call         5 def factorial(x):
    12:34:56.78 line         6     if x <= 1:
    12:34:56.78 line         8     return mul(x, factorial(x - 1))
        ........... x = 2
        12:34:56.78 call         5 def factorial(x):
        12:34:56.78 line         6     if x <= 1:
        12:34:56.78 line         8     return mul(x, factorial(x - 1))
            ........... x = 1
            12:34:56.78 call         5 def factorial(x):
            12:34:56.78 line         6     if x <= 1:
            12:34:56.78 line         7         return 1
            Return value: 1
            ........... a = 2
            ........... b = 1
            12:34:56.78 call        11 def mul(a, b):
            12:34:56.78 line        12     return a * b
            Return value: 2
        Return value: 2
        ........... a = 3
        ........... b = 2
        12:34:56.78 call        11 def mul(a, b):
        12:34:56.78 line        12     return a * b
        Return value: 6
    Return value: 6
    ........... a = 4
    ........... b = 6
    12:34:56.78 call        11 def mul(a, b):
    12:34:56.78 line        12     return a * b
    Return value: 24
Return value: 24
"""
