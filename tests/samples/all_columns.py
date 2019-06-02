from snoop.configuration import Config

snoop = Config(columns='time thread thread_ident file').snoop


@snoop
def main():
    x = 1
    y = x + 2

expected_output = """
12:34:56.78 MainThread 123456789 all_columns.py >>> Call to main in File "/path/to_file.py", line 7
12:34:56.78 MainThread 123456789 all_columns.py    7 | def main():
12:34:56.78 MainThread 123456789 all_columns.py    8 |     x = 1
12:34:56.78 MainThread 123456789 all_columns.py    9 |     y = x + 2
12:34:56.78 MainThread 123456789 all_columns.py .......... y = 3
12:34:56.78 MainThread 123456789 all_columns.py <<< Return value from main: None
"""
