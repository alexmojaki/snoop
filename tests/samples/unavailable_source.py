string = """
import pysnooper

@pysnooper.snoop()
def foo():
    return 3
    
foo()
"""


def main():
    exec(string, {})


expected_output = """
12:34:56.789012 call         4 SOURCE IS UNAVAILABLE
12:34:56.789012 line         6 SOURCE IS UNAVAILABLE
12:34:56.789012 return       6 SOURCE IS UNAVAILABLE
Return value:.. 3
"""
