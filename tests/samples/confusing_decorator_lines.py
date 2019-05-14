import pysnooper


def empty_decorator(function):
    return function


@empty_decorator
@pysnooper.snoop(
    depth=2)  # Multi-line decorator for extra confusion!
@empty_decorator
@empty_decorator
def main():
    str(3)


expected_output = """
12:34:56.78 call        13 def main():
12:34:56.78 line        14     str(3)
<<< Return value from main: None
"""
