from snoop import snoop


@snoop(columns='')
def main():
    x = 1
    y = x + 2


main()

expected_output = """
>>> Call to main in File "/path/to_file.py", line 5
    5 | def main():
    6 |     x = 1
    7 |     y = x + 2
 .......... y = 3
 <<< Return value from main: None
"""
