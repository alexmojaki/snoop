string = """
from snoop import Config

def foo():
    return 3

for color in [False, True]:
    Config(color=color).snoop(foo)()
"""


def main():
    exec(string, {})
