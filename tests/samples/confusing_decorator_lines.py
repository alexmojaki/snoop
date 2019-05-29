import snoop


def empty_decorator(function):
    return function


@empty_decorator
@snoop.snoop(
    depth=2)  # Multi-line decorator for extra confusion!
@empty_decorator
@empty_decorator
def main():
    str(3)


expected_output = """
12:34:56.78 >>> Call to main in File "/path/to_file.py", line 13
12:34:56.78   13 | def main():
12:34:56.78   14 |     str(3)
12:34:56.78 <<< Return value from main: None
"""
