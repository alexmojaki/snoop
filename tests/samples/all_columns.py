import snoop


@snoop(columns='time thread thread_ident file')
def main():
    x = 1
    y = x + 2

main()

expected_output = """
12:34:56.78 MainThread 123456789 all_columns.py >>> Call to main in all_columns.py
12:34:56.78 MainThread 123456789 all_columns.py    5 | def main():
12:34:56.78 MainThread 123456789 all_columns.py    6 |     x = 1
12:34:56.78 MainThread 123456789 all_columns.py    7 |     y = x + 2
12:34:56.78 MainThread 123456789 all_columns.py .......... y = 3
12:34:56.78 MainThread 123456789 all_columns.py <<< Return value from main: None
"""
