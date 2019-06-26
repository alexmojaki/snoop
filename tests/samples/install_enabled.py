import snoop


@snoop
def foo(x):
    return x * 2


def main():
    foo(1)
    snoop.install(enabled=False)
    foo(2)
    snoop.install(enabled=True)
    foo(3)


expected_output = """
12:34:56.78 >>> Call to foo in File "/path/to_file.py", line 5
12:34:56.78 ...... x = 1
12:34:56.78    5 | def foo(x):
12:34:56.78    6 |     return x * 2
12:34:56.78 <<< Return value from foo: 2
12:34:56.78 >>> Call to foo in File "/path/to_file.py", line 5
12:34:56.78 ...... x = 3
12:34:56.78    5 | def foo(x):
12:34:56.78    6 |     return x * 2
12:34:56.78 <<< Return value from foo: 6
"""
