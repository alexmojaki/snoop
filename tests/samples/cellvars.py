def f2(a):
    def f3(a):
        x = 0
        x += 1

        def f4(_a):
            _y = x
            return 42

        return f4(a)

    return f3(a)


def main():
    with snoop(depth=4):
        result1 = f2(42)
    return result1
