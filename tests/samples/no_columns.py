from snoop.configuration import Config

snoop = Config(columns='').snoop


@snoop
def main():
    x = 1
    y = x + 2
