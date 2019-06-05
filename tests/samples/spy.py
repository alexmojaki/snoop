from snoop import spy, pp
from birdseye import eye


@spy()
def foo():
    x = pp(1 + 2)
    y = pp(3 + 4, 5 + 6)[0]
    return x + y


def main():
    foo()
    call_id = eye._last_call_id
    with eye.db.session_scope() as session:
        call = session.query(eye.db.Call).filter_by(id=call_id).one()
        assert call.result == '10'


expected_output = """
12:34:56.78 >>> Call to foo in File "/path/to_file.py", line 6
12:34:56.78    6 | def foo():
12:34:56.78    7 |     x = pp(1 + 2)
12:34:56.78 LOG:
12:34:56.78 .... <argument> = 3
12:34:56.78 .......... x = 3
12:34:56.78    8 |     y = pp(3 + 4, 5 + 6)[0]
12:34:56.78 LOG:
12:34:56.78 .... <argument 1> = 7
12:34:56.78 .... <argument 2> = 11
12:34:56.78 .......... y = 7
12:34:56.78    9 |     return x + y
12:34:56.78 <<< Return value from foo: 10
"""
