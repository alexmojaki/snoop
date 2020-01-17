import snoop


@snoop.snoop()
def main():
    foo = list(range(1000))
    return foo
