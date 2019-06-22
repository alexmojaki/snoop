import snoop


@snoop
def foo(e):
    try:
        if e:
            raise TypeError('bad')
        return
    finally:
        pass


def main():
    foo(0)
    try:
        foo(1)
    except TypeError:
        pass


if __name__ == '__main__':
    main()


expected_output = r"""
12:34:56.78 >>> Call to foo in File "/path/to_file.py", line 5
12:34:56.78 ...... e = 0
12:34:56.78    5 | def foo(e):
12:34:56.78    6 |     try:
12:34:56.78    7 |         if e:
12:34:56.78    9 |         return
12:34:56.78   11 |         pass
12:34:56.78 <<< Return value from foo: None
12:34:56.78 >>> Call to foo in File "/path/to_file.py", line 5
12:34:56.78 ...... e = 1
12:34:56.78    5 | def foo(e):
12:34:56.78    6 |     try:
12:34:56.78    7 |         if e:
12:34:56.78    8 |             raise TypeError('bad')
12:34:56.78 !!! TypeError: bad
12:34:56.78   11 |         pass
12:34:56.78 ??? Call either returned None or ended by exception
"""
