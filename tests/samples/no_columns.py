from snoop.configuration import Config

snoop = Config(columns='').snoop


@snoop
def main():
    x = 1
    y = x + 2


expected_output = """
>>> Call to main in File "/path/to_file.py", line 7
    7 | def main():
    8 |     x = 1
    9 |     y = x + 2
 .......... y = 3
 <<< Return value from main: None
"""
