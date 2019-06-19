from __future__ import print_function

from threading import Thread
from time import sleep

from snoop import Config

snoop = Config(color=True).snoop


def foo():
    raise TypeError


@snoop(depth=2)
def main():
    try:
        (None
         or foo)()
    except:
        pass


def print_output():
    sleep(0.1)
    print(expected_output)


if __name__ == "__main__":
    Thread(target=print_output).start()

expected_output = """
[90m12:34:56.78 [0m[36m[1m>>> Call to [0mmain[36m[1m in [0mFile "/path/to_file.py", line 16
[90m12:34:56.78 [0m[90m  16[0m | def main():
[90m12:34:56.78 [0m[90m  17[0m |     try:
[90m12:34:56.78 [0m[90m  18[0m |         (None
[90m12:34:56.78 [0m[90m  19[0m |          or foo)()
[90m    12:34:56.78 [0m[36m[1m>>> Call to [0mfoo[36m[1m in [0mFile "/path/to_file.py", line 11
[90m    12:34:56.78 [0m[90m  11[0m | def foo():
[90m    12:34:56.78 [0m[90m  12[0m |     raise TypeError
[90m    12:34:56.78 [0m[31m[1m!!! TypeError[0m
[90m    12:34:56.78 [0m[31m[1m!!! Call ended by exception[0m
[90m12:34:56.78 [0m[90m  19[0m |          or foo)()
[90m12:34:56.78 [0m[31m[1m!!! TypeError[0m
[90m12:34:56.78 [0m[90m  20[0m |     except:
[90m12:34:56.78 [0m[90m  21[0m |         pass
[90m12:34:56.78 [0m[32m[1m<<< Return value from main: [0mNone
"""
