import pysnooper


@pysnooper.snoop()
def main():
    x = (
        [
            bar(),  # 1
            bar(),  # 2
        ]
    )
    return x


def bar():
    pass


expected_output = """
12:34:56.78 >>> Call to main in multiline.py
12:34:56.78    5 | def main():
12:34:56.78    6 |     x = (
12:34:56.78    7 |         [
12:34:56.78    8 |             bar(),  # 1
12:34:56.78    9 |             bar(),  # 2
12:34:56.78 .......... x = [None, None]
12:34:56.78   12 |     return x
12:34:56.78 <<< Return value from main: [None, None]
"""
