import snoop
from contextlib import contextmanager

@snoop.snoop()
def main():
    x = (
        [
            bar(),  # 1
            bar(),  # 2
        ]
    )

    with context(
            bar(),  # 1
            bar(),  # 2
    ):
        try:
            for _ in [
                bar(
                    bar(),  # 1
                    bar(),  # 2
                )
            ]:
                while bar(
                        bar(),  # 1
                        bar(),  # 2
                ):
                    pass
                else:
                    bar()
            else:
                bar()
                raise ValueError
        except (
                ValueError,
                TypeError,
        ):
            pass
        finally:
            bar(
                [
                    bar(),  # 1
                    bar(),  # 2
                ]
            )

    with context(
            bar(),  # 1
            bar(),  # 2
    ):
        if bar(
                bar(),  # 1
                bar(),  # 2
        ):
            pass
        elif [
            bar(
                bar(),  # 1
                bar(),  # 2
            )
        ]:
            pass

    return x


def bar(*_):
    pass


@contextmanager
def context(*_):
    yield
