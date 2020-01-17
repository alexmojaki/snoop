from snoop.configuration import Config

snoop = Config(columns='time thread thread_ident file full_file function function_qualname').snoop


def main():
    @snoop
    def foo():
        x = 1
        y = x + 2

    foo()
