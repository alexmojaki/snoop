from snoop.configuration import Config

from birdseye import eye

config = Config(enabled=False)


@config.spy
def foo():
    assert config.pp(1 + 2) == 3
    assert config.pp(1 + 3, 6) == (4, 6)

def main():
    call_id = eye._last_call_id
    foo()
    assert call_id is call_id
