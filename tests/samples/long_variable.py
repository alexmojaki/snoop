import snoop


@snoop.snoop()
def main():
    return list(range(1000))
