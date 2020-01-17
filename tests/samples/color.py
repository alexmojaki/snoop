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
    pp(
        [
            x + y
            for x, y in zip(range(1000, 1020), range(2000, 2020))
        ]
    )
