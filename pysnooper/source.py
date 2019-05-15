import ast
import re
from collections import defaultdict

import six

from pysnooper import utils


class Source(object):
    def __init__(self, lines):
        self.lines = lines
        if not isinstance(lines, list):
            self.statements = defaultdict(lambda: None)
            return

        self.statements = {}

        nodes_by_line = defaultdict(list)
        for node in ast.walk(ast.parse('\n'.join(lines))):
            for child in ast.iter_child_nodes(node):
                child.parent = node
            if hasattr(node, 'lineno'):
                nodes_by_line[node.lineno].append(node)

        for lineno, nodes in nodes_by_line.items():
            stmts = {
                statement_containing_node(node)
                for node in nodes_by_line[lineno]
            }
            if len(stmts) == 1:
                stmt = list(stmts)[0]
            else:
                stmt = None
            self.statements[lineno] = stmt


def statement_containing_node(node):
    while not isinstance(node, ast.stmt):
        node = node.parent
    return node


class UnavailableSource(object):
    def __getitem__(self, i):
        return u'SOURCE IS UNAVAILABLE'


source_cache = {}
ipython_filename_pattern = re.compile('^<ipython-input-([0-9]+)-.*>$')


def get_source_from_frame(frame):
    globs = frame.f_globals or {}
    module_name = globs.get('__name__')
    file_name = frame.f_code.co_filename
    cache_key = (module_name, file_name)
    try:
        return source_cache[cache_key]
    except KeyError:
        pass
    loader = globs.get('__loader__')

    source = None
    if hasattr(loader, 'get_source'):
        try:
            source = loader.get_source(module_name)
        except ImportError:
            pass
        if source is not None:
            source = source.splitlines()
    if source is None:
        ipython_filename_match = ipython_filename_pattern.match(file_name)
        if ipython_filename_match:
            entry_number = int(ipython_filename_match.group(1))
            try:
                import IPython
                ipython_shell = IPython.get_ipython()
                ((_, _, source_chunk),) = ipython_shell.history_manager. \
                    get_range(0, entry_number, entry_number + 1)
                source = source_chunk.splitlines()
            except Exception:
                pass
        else:
            try:
                with open(file_name, 'rb') as fp:
                    source = fp.read().splitlines()
            except utils.file_reading_errors:
                pass
    if source is None:
        source = UnavailableSource()

    # If we just read the source from a file, or if the loader did not
    # apply tokenize.detect_encoding to decode the source into a
    # string, then we should do that ourselves.
    if isinstance(source[0], bytes):
        encoding = 'ascii'
        for line in source[:2]:
            # File coding may be specified. Match pattern from PEP-263
            # (https://www.python.org/dev/peps/pep-0263/)
            match = re.search(br'coding[:=]\s*([-\w.]+)', line)
            if match:
                encoding = match.group(1).decode('ascii')
                break
        source = [six.text_type(sline, encoding, 'replace') for sline in
                  source]

    source = Source(source)

    source_cache[cache_key] = source
    return source
