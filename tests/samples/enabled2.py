from snoop.configuration import Config

config = Config(enabled=False)

# This test leaves out spy for the NO_ASTTOKENS versions,
# but other versions can test it too

@config.snoop
def main():
    assert config.pp(1 + 2) == 3
    assert config.pp(1 + 3, 6) == (4, 6)
