import pysnooper


def main():
    my_function = pysnooper.snoop()(lambda x: x ** 2)
    my_function(3)


if __name__ == '__main__':
    main()

expected_output = """
........... x = 3
12:34:56.78 call         5     my_function = pysnooper.snoop()(lambda x: x ** 2)
12:34:56.78 line         5     my_function = pysnooper.snoop()(lambda x: x ** 2)
Return value: 9
"""
