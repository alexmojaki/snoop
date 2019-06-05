from threading import Thread

from snoop.configuration import Config

snoop = Config(columns='thread').snoop


@snoop
def foo():
    return 1


def run(name):
    thread = Thread(target=foo, name=name)
    thread.start()
    thread.join()


def main():
    run('short')
    run('longername')
    run('short')


expected_output = """
short >>> Call to foo in File "/path/to_file.py", line 9
short    9 | def foo():
short   10 |     return 1
short <<< Return value from foo: 1
longername >>> Call to foo in File "/path/to_file.py", line 9
longername    9 | def foo():
longername   10 |     return 1
longername <<< Return value from foo: 1
short      >>> Call to foo in File "/path/to_file.py", line 9
short         9 | def foo():
short        10 |     return 1
short      <<< Return value from foo: 1
"""
