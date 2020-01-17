from snoop import pp


def main():
    x = 1
    assert pp.deep(lambda: "a" + f"b {x} c") == "ab 1 c"
    assert pp.deep(lambda: "a" + f"b {x} {x * 2} c") == "ab 1 2 c"
