from __future__ import print_function

from snoop import Config

config = Config(color=True)
snoop = config.snoop
pp = config.pp


def foo():
    raise TypeError


@snoop(depth=2)
def main():
    try:
        (None
         or foo)()
    except:
        pass
    x = 1
    y = 2
    pp(
        [
            x + y
        ]
    )
