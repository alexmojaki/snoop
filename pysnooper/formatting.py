import opcode
import os
import re
import threading
import traceback
from datetime import datetime

from cheap_repr import cheap_repr
import six
from pysnooper.utils import ensure_tuple, truncate_string, truncate_list

from . import utils


class Event(object):
    def __init__(self, frame, event, arg, depth):
        self.frame = frame
        self.event = event
        self.arg = arg
        self.depth = depth

        self.variables = []
        self.source = get_source_from_frame(self.frame)
        self.line_no = self.frame.f_lineno

        if self.event == 'call' and self.source_line.lstrip().startswith('@'):
            # If a function decorator is found, skip lines until an actual
            # function definition is found.
            while True:
                self.line_no += 1
                try:
                    if self.source_line.lstrip().startswith('def'):
                        break
                except IndexError:
                    self.line_no = self.frame.lineno
                    break

    @property
    def source_line(self):
        return self.source[self.line_no - 1]


class DefaultFormatter(object):
    datetime_format = None

    def __init__(self, prefix='', columns='time'):
        self.prefix = six.text_type(prefix)
        self.columns = [
            column if callable(column) else
            getattr(self, '{}_column'.format(column))
            for column in ensure_tuple(columns)
        ]
        self.column_widths = dict.fromkeys(self.columns, 0)
        self.total_width = 0

    def thread_column(self, _event):
        return threading.current_thread().name

    def thread_ident_column(self, _event):
        return threading.current_thread().ident

    def time_column(self, _event):
        datetime_format = self.datetime_format or '%H:%M:%S.%f'
        result = datetime.now().strftime(datetime_format)
        if self.datetime_format is None:
            result = result[:-4]
        return result

    def file_column(self, event):
        result = os.path.basename(event.frame.f_code.co_filename)
        if result.endswith('.pyc'):
            result = result[:-1]
        return result

    def function_column(self, event):
        return event.frame.f_code.co_name

    def format(self, event):
        indent = event.depth * u'    '
        self.columns_string(event)
        self.total_width = max(
            len(self.columns_string(event)),
            self.total_width,
        )
        lines = [
            self.format_variable(var)
            for var in event.variables
        ]
        
        if event.event == 'return':
            # If a call ends due to an exception, we still get a 'return' event
            # with arg = None. This seems to be the only way to tell the difference
            # https://stackoverflow.com/a/12800909/2482744
            code_byte = event.frame.f_code.co_code[event.frame.f_lasti]
            if not isinstance(code_byte, int):
                code_byte = ord(code_byte)
            if (event.arg is None
                    and opcode.opname[code_byte]
                    not in ('RETURN_VALUE', 'YIELD_VALUE')):
                lines += [u'!!! Call ended by exception']
            else:
                lines += [self.format_return_value(event.arg)]
        elif event.event == 'exception':
            exception_string = ''.join(traceback.format_exception_only(*event.arg[:2]))
            lines += truncate_list(
                ['!!! ' + truncate_string(line, 200)
                 for line in exception_string.splitlines()],
                max_length=5,
            )
        else:
            lines += [self.format_event(event)]
            
        return ''.join([
            (
                    self.prefix
                    + indent
                    + line
                    + u'\n'
            )
            for line in lines
        ])

    def columns_string(self, event):
        column_strings = []
        for column in self.columns:
            string = six.text_type(column(event))
            width = self.column_widths[column] = max(
                self.column_widths[column],
                len(string),
            )
            column_strings.append(string.ljust(width))
        return u' '.join(column_strings)

    def format_event(self, entry):
        return u'{columns_string} {event:9} {line_no:4} {source_line}'.format(
            source_line=entry.source_line,
            columns_string=self.columns_string(entry),
            **entry.__dict__
        )

    def format_variable(self, entry):
        return u'{dots} {} = {}'.format(
            *entry,
            dots=self.total_width * u'.',
        )

    def format_return_value(self, value):
        return u'{description} {value_repr}'.format(
            description=u'Return value:'.ljust(self.total_width, '.'),
            value_repr=cheap_repr(value),
        )


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

    source_cache[cache_key] = source
    return source
