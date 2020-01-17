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
