import snoop


def empty_decorator(function):
    return function


@empty_decorator
@snoop.snoop(
    depth=2)  # Multi-line decorator for extra confusion!
@empty_decorator
@empty_decorator
def main():
    str(3)
