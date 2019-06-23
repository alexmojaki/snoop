import snoop


def f4(x4):
    result4 = snoop.pp(x4 * 2)
    return result4


def f3(x3):
    result3 = f4(x3)
    return result3


def f2(x2):
    result2 = f3(x2)
    return result2


@snoop(depth=3)
def _main():
    result1 = f2(8)
    return result1


def main():
    import snoop.pp_module
    before = snoop.pp_module.NO_ASTTOKENS
    snoop.pp_module.NO_ASTTOKENS = True
    try:
        _main()
    finally:
        snoop.pp_module.NO_ASTTOKENS = before


if __name__ == '__main__':
    main()


expected_output = """
12:34:56.78 >>> Call to _main in File "/path/to_file.py", line 20
12:34:56.78   20 | def _main():
12:34:56.78   21 |     result1 = f2(8)
    12:34:56.78 >>> Call to f2 in File "/path/to_file.py", line 14
    12:34:56.78 ...... x2 = 8
    12:34:56.78   14 | def f2(x2):
    12:34:56.78   15 |     result2 = f3(x2)
        12:34:56.78 >>> Call to f3 in File "/path/to_file.py", line 9
        12:34:56.78 ...... x3 = 8
        12:34:56.78    9 | def f3(x3):
        12:34:56.78   10 |     result3 = f4(x3)
        12:34:56.78 LOG:
        12:34:56.78 .... <argument> = 16
        12:34:56.78 .......... result3 = 16
        12:34:56.78   11 |     return result3
        12:34:56.78 <<< Return value from f3: 16
    12:34:56.78   15 |     result2 = f3(x2)
    12:34:56.78 .......... result2 = 16
    12:34:56.78   16 |     return result2
    12:34:56.78 <<< Return value from f2: 16
12:34:56.78   21 |     result1 = f2(8)
12:34:56.78 .......... result1 = 16
12:34:56.78   22 |     return result1
12:34:56.78 <<< Return value from _main: 16
"""
