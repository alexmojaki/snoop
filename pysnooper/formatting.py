import opcode
import threading
import traceback
from datetime import datetime

import six
from cheap_repr import cheap_repr

from pysnooper.pycompat import try_statement
from pysnooper.source import get_source_from_frame
from pysnooper.utils import ensure_tuple, truncate_string, truncate_list, short_filename


class Event(object):
    def __init__(self, frame, event, arg, depth, line_no=None, last_line_no=None):
        self.frame = frame
        self.event = event
        self.arg = arg
        self.depth = depth

        self.variables = []
        self.source = get_source_from_frame(self.frame)
        if line_no is None:
            line_no = frame.f_lineno
        self.line_no = line_no
        self.last_line_no = last_line_no

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
        return self.source.lines[self.line_no - 1]


class DefaultFormatter(object):
    datetime_format = None

    def __init__(self, prefix='', columns='time'):
        prefix = six.text_type(prefix)
        if prefix and prefix == prefix.rstrip():
            prefix += ' '
        self.prefix = prefix
        self.columns = [
            column if callable(column) else
            getattr(self, '{}_column'.format(column))
            for column in ensure_tuple(columns, split=True)
        ]
        self.column_widths = dict.fromkeys(self.columns, 0)

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
        return short_filename(event.frame.f_code)

    def function_column(self, event):
        return event.frame.f_code.co_name

    def full_prefix(self, event):
        return (
                self.prefix
                + event.depth * u'    '
                + self.columns_string(event)
                + ' '
        )

    def format(self, event):
        prefix = self.full_prefix(event)

        lines = []
        dots = ''
        statement_start_lines = []
        
        if event.event == 'call':
            lines += [u'>>> Call to {} in {}'.format(
                event.frame.f_code.co_name,
                short_filename(event.frame.f_code),
            )]

        statements = event.source.statements
        last_statement = statements[event.last_line_no]
        if last_statement:
            last_lineno = last_statement.lineno
            last_source_line = event.source.lines[last_lineno - 1]
            spaces = get_leading_spaces(last_source_line)
            dots = spaces.replace(' ', '.').replace('\t', '....')
            if event.event != 'call':
                this_statement = statements[event.line_no]

                if (
                        this_statement != last_statement and
                        this_statement.lineno != event.line_no and
                        not isinstance(this_statement, try_statement)
                ):
                    original_line_no = event.line_no
                    for n in range(this_statement.lineno, original_line_no):
                        event.line_no = n
                        statement_start_lines.append(self.format_event(event))
                    event.line_no = original_line_no
                    
        lines += [
            self.format_variable(var, dots)
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
                lines += [self.format_return_value(event)]
        elif event.event == 'exception':
            exception_string = ''.join(traceback.format_exception_only(*event.arg[:2]))
            lines += truncate_list(
                ['!!! ' + truncate_string(line, 200)
                 for line in exception_string.splitlines()],
                max_length=5,
            )
        else:
            lines += statement_start_lines + [self.format_event(event)]
        return ''.join([
            (
                    prefix
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
        return u'{line_no:4} | {source_line}'.format(
            source_line=entry.source_line,
            **entry.__dict__
        )

    def format_variable(self, entry, dots):
        return u'......{dots} {} = {}'.format(*entry, dots=dots)

    def format_return_value(self, event):
        return u'<<< Return value from {func}: {value}'.format(
            func=event.frame.f_code.co_name,
            value=cheap_repr(event.arg),
        )

    def format_line_only(self, event):
        return (
                self.full_prefix(event)
                + self.format_event(event)
                + u'\n'
        )

def get_leading_spaces(s):
    return s[:len(s) - len(s.lstrip())]
