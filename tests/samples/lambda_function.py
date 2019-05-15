import pysnooper


def main():
    my_function = pysnooper.snoop()(lambda x: x ** 2)
    my_function(3)


if __name__ == '__main__':
    main()

expected_output = """
12:34:56.78 >>> Call to <lambda> in lambda_function.py
12:34:56.78 .......... x = 3
12:34:56.78    5 |     my_function = pysnooper.snoop()(lambda x: x ** 2)
12:34:56.78    5 |     my_function = pysnooper.snoop()(lambda x: x ** 2)
12:34:56.78 <<< Return value from <lambda>: 9
"""
