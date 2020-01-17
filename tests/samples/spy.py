
from birdseye import eye


@spy(depth=4)
def foo():
    x = pp.deep(lambda: 1 + 2)
    y = pp(3 + 4, 5 + 6)[0]
    return x + y


# Testing spy with and without parentheses
@spy
def bar():
    result = pp(4 + 6, 7 + 8)
    return result[0]


def main():
    for func in [foo, bar]:
        func()
        call_id = eye._last_call_id
        with eye.db.session_scope() as session:
            call = session.query(eye.db.Call).filter_by(id=call_id).one()
            assert call.result == '10'
