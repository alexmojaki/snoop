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
[90m12:34:56.78 [0m[36m[1m>>> Call to main in File "/path/to_file.py", line 16[0m
[90m12:34:56.78 [0m[90m  16[0m | [38;5;81mdef[39m[38;5;231m [39m[38;5;148mmain[39m[38;5;231m([39m[38;5;231m)[39m[38;5;231m:[39m
[90m12:34:56.78 [0m[90m  17[0m | [38;5;231m    [39m[38;5;81mtry[39m[38;5;231m:[39m
[90m12:34:56.78 [0m[90m  18[0m | [38;5;231m        [39m[38;5;231m([39m[38;5;81mNone[39m
[90m12:34:56.78 [0m[90m  19[0m | [38;5;231m         [39m[38;5;197mor[39m[38;5;231m [39m[38;5;231mfoo[39m[38;5;231m)[39m[38;5;231m([39m[38;5;231m)[39m
[90m    12:34:56.78 [0m[36m[1m>>> Call to foo in File "/path/to_file.py", line 11[0m
[90m    12:34:56.78 [0m[90m  11[0m | [38;5;81mdef[39m[38;5;231m [39m[38;5;148mfoo[39m[38;5;231m([39m[38;5;231m)[39m[38;5;231m:[39m
[90m    12:34:56.78 [0m[90m  12[0m | [38;5;231m    [39m[38;5;81mraise[39m[38;5;231m [39m[38;5;148mTypeError[39m
[90m    12:34:56.78 [0m[31m[1m!!! TypeError[0m
[90m    12:34:56.78 [0m[31m[1m!!! Call ended by exception[0m
[90m12:34:56.78 [0m[90m  19[0m | [38;5;231m         [39m[38;5;197mor[39m[38;5;231m [39m[38;5;231mfoo[39m[38;5;231m)[39m[38;5;231m([39m[38;5;231m)[39m
[90m12:34:56.78 [0m[31m[1m!!! TypeError[0m
[90m12:34:56.78 [0m[90m  20[0m | [38;5;231m    [39m[38;5;81mexcept[39m[38;5;231m:[39m
[90m12:34:56.78 [0m[90m  21[0m | [38;5;231m        [39m[38;5;81mpass[39m
[90m12:34:56.78 [0m[32m[1m<<< Return value from main: [0m[38;5;81mNone[39m
"""
