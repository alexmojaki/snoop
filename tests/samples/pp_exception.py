from tests.test_snoop import sample_traceback


@snoop
def main():
    x = 1
    y = 2
    try:
        pp.deep(lambda: x + y + bad() + 2)
    except:
        sample_traceback()


def bad():
    raise TypeError('bad')
