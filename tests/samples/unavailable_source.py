string = """
from snoop import snoop

@snoop()
def foo():
    return 3
    
foo()
"""


def main():
    exec(string, {})


expected_output = """
12:34:56.78 >>> Call to foo in File "/path/to_file.py", line 4
12:34:56.78    4 | SOURCE IS UNAVAILABLE
12:34:56.78    6 | SOURCE IS UNAVAILABLE
12:34:56.78 <<< Return value from foo: 3
"""
