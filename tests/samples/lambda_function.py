import snoop


def main():
    my_function = snoop.snoop()(lambda x: x ** 2)
    my_function(3)


if __name__ == '__main__':
    main()

expected_output = """
12:34:56.78 >>> Call to <lambda> in File "/path/to_file.py", line 5
12:34:56.78 .......... x = 3
12:34:56.78    5 |     my_function = snoop.snoop()(lambda x: x ** 2)
12:34:56.78    5 |     my_function = snoop.snoop()(lambda x: x ** 2)
12:34:56.78 <<< Return value from <lambda>: 9
"""
