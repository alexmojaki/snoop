from snoop.configuration import Config

from birdseye import eye

config = Config(enabled=False)


@config.spy
def foo():
    assert config.pp(1 + 2) == 3


def main():
    call_id = eye._last_call_id
    foo()
    assert call_id is eye._last_call_id


expected_output = """
"""
