import pysnooper


@pysnooper.snoop()
def main():
    foo = list(range(1000))
    return foo


expected_output = """
12:34:56.789012 call         5 def main():
12:34:56.789012 line         6     foo = list(range(1000))
New var:....... foo = [0, 1, 2, ..., 997, 998, 999]
12:34:56.789012 line         7     return foo
12:34:56.789012 return       7     return foo
Return value:.. [0, 1, 2, ..., 997, 998, 999]
"""
