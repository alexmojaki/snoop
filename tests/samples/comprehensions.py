


@snoop()
def foo(x):
    return x ** 2


def no_trace(_x):
    return 3


@snoop(depth=2)
def bar():
    str([no_trace(x) for x in [1, 2]])


@snoop()
def main():
    str([x for x in range(100)])
    str({x for x in range(100)})
    str({x: x for x in range(100)})
    str([[x + y for x in range(3)] for y in range(3)])
    str([foo(x) for x in [1, 2]])
    str([no_trace(x) for x in [1, 2]])
    bar()


expected_output = """
12:34:56.78 >>> Call to main in File "/path/to_file.py", line 19
12:34:56.78   19 | def main():
12:34:56.78   20 |     str([x for x in range(100)])
    12:34:56.78 List comprehension:
    12:34:56.78   20 |     str([x for x in range(100)])
    12:34:56.78 .......... Iterating over <range_iterator object at 0xABC>
    12:34:56.78 .......... Values of x: 0, 1, 2, 3, 4, ..., 95, 96, 97, 98, 99
    12:34:56.78 Result: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, ..., 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
12:34:56.78   20 |     str([x for x in range(100)])
12:34:56.78   21 |     str({x for x in range(100)})
    12:34:56.78 Set comprehension:
    12:34:56.78   21 |     str({x for x in range(100)})
    12:34:56.78 .......... Iterating over <range_iterator object at 0xABC>
    12:34:56.78 .......... Values of x: 0, 1, 2, 3, 4, ..., 95, 96, 97, 98, 99
    12:34:56.78 Result: {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, ...}
12:34:56.78   21 |     str({x for x in range(100)})
12:34:56.78   22 |     str({x: x for x in range(100)})
    12:34:56.78 Dict comprehension:
    12:34:56.78   22 |     str({x: x for x in range(100)})
    12:34:56.78 .......... Iterating over <range_iterator object at 0xABC>
    12:34:56.78 .......... Values of x: 0, 1, 2, 3, 4, ..., 95, 96, 97, 98, 99
    12:34:56.78 Result: {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, ...}
12:34:56.78   22 |     str({x: x for x in range(100)})
12:34:56.78   23 |     str([[x + y for x in range(3)] for y in range(3)])
    12:34:56.78 List comprehension:
    12:34:56.78   23 |     str([[x + y for x in range(3)] for y in range(3)])
        12:34:56.78 List comprehension:
        12:34:56.78   23 |     str([[x + y for x in range(3)] for y in range(3)])
        12:34:56.78 .......... Iterating over <range_iterator object at 0xABC>
        12:34:56.78 .......... Values of y: 0
        12:34:56.78 .......... Values of x: 0, 1, 2
        12:34:56.78 Result: [0, 1, 2]
    12:34:56.78   23 |     str([[x + y for x in range(3)] for y in range(3)])
        12:34:56.78 List comprehension:
        12:34:56.78   23 |     str([[x + y for x in range(3)] for y in range(3)])
        12:34:56.78 .......... Iterating over <range_iterator object at 0xABC>
        12:34:56.78 .......... Values of y: 1
        12:34:56.78 .......... Values of x: 0, 1, 2
        12:34:56.78 Result: [1, 2, 3]
    12:34:56.78   23 |     str([[x + y for x in range(3)] for y in range(3)])
        12:34:56.78 List comprehension:
        12:34:56.78   23 |     str([[x + y for x in range(3)] for y in range(3)])
        12:34:56.78 .......... Iterating over <range_iterator object at 0xABC>
        12:34:56.78 .......... Values of y: 2
        12:34:56.78 .......... Values of x: 0, 1, 2
        12:34:56.78 Result: [2, 3, 4]
    12:34:56.78   23 |     str([[x + y for x in range(3)] for y in range(3)])
    12:34:56.78 .......... Iterating over <range_iterator object at 0xABC>
    12:34:56.78 .......... Values of y: 0, 1, 2
    12:34:56.78 Result: [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
12:34:56.78   23 |     str([[x + y for x in range(3)] for y in range(3)])
12:34:56.78   24 |     str([foo(x) for x in [1, 2]])
    12:34:56.78 List comprehension:
    12:34:56.78   24 |     str([foo(x) for x in [1, 2]])
        12:34:56.78 >>> Call to foo in File "/path/to_file.py", line 5
        12:34:56.78 ...... x = 1
        12:34:56.78    5 | def foo(x):
        12:34:56.78    6 |     return x ** 2
        12:34:56.78 <<< Return value from foo: 1
    12:34:56.78   24 |     str([foo(x) for x in [1, 2]])
        12:34:56.78 >>> Call to foo in File "/path/to_file.py", line 5
        12:34:56.78 ...... x = 2
        12:34:56.78    5 | def foo(x):
        12:34:56.78    6 |     return x ** 2
        12:34:56.78 <<< Return value from foo: 4
    12:34:56.78   24 |     str([foo(x) for x in [1, 2]])
    12:34:56.78 .......... Iterating over <tuple_iterator object at 0xABC>
    12:34:56.78 .......... Values of x: 1, 2
    12:34:56.78 Result: [1, 4]
12:34:56.78   24 |     str([foo(x) for x in [1, 2]])
12:34:56.78   25 |     str([no_trace(x) for x in [1, 2]])
    12:34:56.78 List comprehension:
    12:34:56.78   25 |     str([no_trace(x) for x in [1, 2]])
    12:34:56.78 .......... Iterating over <tuple_iterator object at 0xABC>
    12:34:56.78 .......... Values of x: 1, 2
    12:34:56.78 Result: [3, 3]
12:34:56.78   25 |     str([no_trace(x) for x in [1, 2]])
12:34:56.78   26 |     bar()
    12:34:56.78 >>> Call to bar in File "/path/to_file.py", line 14
    12:34:56.78   14 | def bar():
    12:34:56.78   15 |     str([no_trace(x) for x in [1, 2]])
        12:34:56.78 List comprehension:
        12:34:56.78   15 |     str([no_trace(x) for x in [1, 2]])
            12:34:56.78 >>> Call to no_trace in File "/path/to_file.py", line 9
            12:34:56.78 ...... _x = 1
            12:34:56.78    9 | def no_trace(_x):
            12:34:56.78   10 |     return 3
            12:34:56.78 <<< Return value from no_trace: 3
        12:34:56.78   15 |     str([no_trace(x) for x in [1, 2]])
            12:34:56.78 >>> Call to no_trace in File "/path/to_file.py", line 9
            12:34:56.78 ...... _x = 2
            12:34:56.78    9 | def no_trace(_x):
            12:34:56.78   10 |     return 3
            12:34:56.78 <<< Return value from no_trace: 3
        12:34:56.78   15 |     str([no_trace(x) for x in [1, 2]])
        12:34:56.78 .......... Iterating over <tuple_iterator object at 0xABC>
        12:34:56.78 .......... Values of x: 1, 2
        12:34:56.78 Result: [3, 3]
    12:34:56.78   15 |     str([no_trace(x) for x in [1, 2]])
    12:34:56.78 <<< Return value from bar: None
12:34:56.78   26 |     bar()
12:34:56.78 <<< Return value from main: None
"""
