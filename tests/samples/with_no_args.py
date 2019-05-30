import snoop


def main():
    x = 1
    with snoop:
        result = 2 + 2


expected_output = """
12:34:56.78 >>> Enter with block in main in File "/path/to_file.py", line 6
12:34:56.78 .......... x = 1
12:34:56.78    7 |         result = 2 + 2
12:34:56.78 .............. result = 4
12:34:56.78 <<< Exit with block in main
"""
