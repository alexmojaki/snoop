import snoop


def main():
    x = 1
    with snoop:
        result = 2 + 2

    snoop.pp(x)
