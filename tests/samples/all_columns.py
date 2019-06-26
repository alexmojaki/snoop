from snoop.configuration import Config

snoop = Config(columns='time thread thread_ident file full_file function function_qualname').snoop


def main():
    @snoop
    def foo():
        x = 1
        y = x + 2

    foo()


expected_output = """
12:34:56.78 MainThread 123456789 all_columns.py /path/to_file.py foo main.<locals>.foo >>> Call to main.<locals>.foo in File "/path/to_file.py", line 8
12:34:56.78 MainThread 123456789 all_columns.py /path/to_file.py foo main.<locals>.foo    8 |     def foo():
12:34:56.78 MainThread 123456789 all_columns.py /path/to_file.py foo main.<locals>.foo    9 |         x = 1
12:34:56.78 MainThread 123456789 all_columns.py /path/to_file.py foo main.<locals>.foo   10 |         y = x + 2
12:34:56.78 MainThread 123456789 all_columns.py /path/to_file.py foo main.<locals>.foo .............. y = 3
12:34:56.78 MainThread 123456789 all_columns.py /path/to_file.py foo main.<locals>.foo <<< Return value from main.<locals>.foo: None
"""
