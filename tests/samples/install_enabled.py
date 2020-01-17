import snoop


@snoop
def foo(x):
    return x * 2


def main():
    foo(1)
    snoop.install(enabled=False)
    foo(2)
    snoop.install(enabled=True)
    foo(3)
