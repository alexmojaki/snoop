
from datetime import datetime
import sys

def test_misc():
    x = 1
    y = 2
    assert pp(pp(x) + y) == 3
    assert pp.deep(lambda: (x + y) + y) == 5

    with snoop:
        y = 3  # custom pformat is not used here

def test_larger_object():
    d = [
        'a long key to be pretty printed prettily',
        [
            'prettyprinter prints datetime with keyword arguments:',
            datetime.utcfromtimestamp(42),
        ]
    ]
    pp(d)

def main():
    sys.stderr.write(u'\nTest with custom pformat\n')
    snoop.install(pformat=lambda x: 'custom(' + repr(x) + ')')
    test_misc()
    test_larger_object()

    sys.stderr.write(u'\nTest without prettyprinter and without pprintpp\n')
    sys.modules['prettyprinter'] = {}
    sys.modules['pprintpp'] = {}
    snoop.install()
    test_larger_object()

    sys.stderr.write(u'\nTest with prettyprinter and without pprintpp\n')
    del sys.modules['prettyprinter']
    sys.modules['pprintpp'] = {}
    snoop.install()
    test_larger_object()

    sys.stderr.write(u'\nTest without prettyprinter and with pprintpp\n')
    sys.modules['prettyprinter'] = {}
    del sys.modules['pprintpp']
    snoop.install()
    test_larger_object()

    sys.stderr.write(u'\nTest with prettyprinter and with pprintpp\n')
    del sys.modules['prettyprinter']
    del sys.modules['pprintpp']
    snoop.install()
    test_larger_object()

    # clear 3rd party packages afterwards
    sys.modules['prettyprinter'] = {}
    sys.modules['pprintpp'] = {}
    snoop.install()

