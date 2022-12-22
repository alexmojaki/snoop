import ast
import threading
import traceback
from collections import defaultdict
from datetime import datetime
from textwrap import dedent

import executing
import opcode
import six
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.python import Python3Lexer
from pygments.styles.monokai import MonokaiStyle
from six import PY3

from snoop.utils import (NO_ASTTOKENS, ArgDefaultDict, FormattedValue,
                         ensure_tuple, lru_cache, my_cheap_repr,
                         optional_numeric_label, short_filename, try_statement)

try:
    from pygments.lexers.python import Python2Lexer
except ImportError:
    from pygments.lexers.python import PythonLexer as Python2Lexer


class StatementsDict(dict):
    def __init__(self, source):
        super(StatementsDict, self).__init__()
        self.source = source

    def __missing__(self, key):
        statements = self.source.statements_at_line(key)
        if len(statements) == 1:
            result = list(statements)[0]
        else:
            result = None
        self[key] = result
        return result


class Source(executing.Source):
    def __init__(self, *args, **kwargs):
        super(Source, self).__init__(*args, **kwargs)
        if self.tree and self.text:
            self.highlighted = ArgDefaultDict(
                lambda style: raw_highlight(self.text, style).splitlines()
            )
        else:
            self.lines = defaultdict(lambda: u'SOURCE IS UNAVAILABLE')
            self.highlighted = defaultdict(lambda: self.lines)
        self.statements = StatementsDict(self)
        self.nodes = []
        if self.tree:
            self.tree._depth = 0
            for node in ast.walk(self.tree):
                node._tree_index = len(self.nodes)
                self.nodes.append(node)
                for child in ast.iter_child_nodes(node):
                    child._depth = node._depth + 1

    def get_text_with_indentation(self, node):
        result = self.asttokens().get_text(node)

        if not result:
            if isinstance(node, FormattedValue):
                fvals = [
                    n for n in node.parent.values
                    if isinstance(n, FormattedValue)
                ]
                return u'<f-string value{}>'.format(
                    optional_numeric_label(
                        fvals.index(node),
                        fvals,
                    )
                )
            else:
                return "<unknown>"

        if '\n' in result:
            result = ' ' * node.first_token.start[1] + result
            result = dedent(result)
        else:
            result = result.strip()
        return result


lexer = (Python3Lexer if PY3 else Python2Lexer)(stripnl=False)


class ForceWhiteTerminal256Formatter(Terminal256Formatter):
    def _closest_color(self, r, g, b):
        result = super(ForceWhiteTerminal256Formatter, self)._closest_color(r, g, b)
        if result == 15:
            result += 6 ** 3
        return result


class NeutralMonokaiStyle(MonokaiStyle):
    """
    Monokai style that is somewhat readable on both dark and light backgrounds
    by replacing 'white' styles with no style so that the terminal can automatically
    use the appropriate foreground color.
    """
    styles = {
        k: '' if v == '#f8f8f2' else v
        for k, v in MonokaiStyle.styles.items()
    }


formatters = ArgDefaultDict(lambda style: ForceWhiteTerminal256Formatter(style=style))


def raw_highlight(code, style):
    return highlight(code, lexer, formatters[style])


cached_highlight = lru_cache(maxsize=1024)(raw_highlight)


class Event(object):
    def __init__(self, frame_info, event, arg, depth, line_no=None):
        self.frame_info = frame_info
        self.frame = frame = frame_info.frame
        self.source = frame_info.source
        self.last_line_no = frame_info.last_line_no
        self.comprehension_type = frame_info.comprehension_type

        self.event = event
        self.arg = arg
        self.depth = depth

        self.variables = []
        if line_no is None:
            line_no = frame.f_lineno
        self.line_no = line_no
        self.code = frame.f_code

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

    def code_qualname(self):
        return self.source.code_qualname(self.code)

    def opname_at(self, index):
        code_byte = self.code.co_code[index]
        if not isinstance(code_byte, int):
            code_byte = ord(code_byte)
        return opcode.opname[code_byte]

    @property
    def opname(self):
        return self.opname_at(self.frame.f_lasti)

    @property
    def is_yield_value(self):
        for i in range(self.frame.f_lasti, -1, -1):
            opname = self.opname_at(i)
            if opname not in ('RESUME', 'CACHE'):
                return opname == 'YIELD_VALUE'


class DefaultFormatter(object):
    datetime_format = None

    def __init__(self, prefix, columns, color):
        prefix = six.text_type(prefix)
        if prefix and prefix == prefix.rstrip():
            prefix += u' '
        self.prefix = prefix
        self.columns = [
            column if callable(column) else
            getattr(self, u'{}_column'.format(column))
            for column in ensure_tuple(columns, split=True)
        ]
        self.column_widths = dict.fromkeys(self.columns, 0)
        if color is True:
            color = NeutralMonokaiStyle
        if color:
            self.c = Colors
            self.c.grey = formatters[color].style_string["Token.Comment"][0]

            def highlighted(code):
                return cached_highlight(code, color)

            def highlighted_source_line(event):
                return event.source.highlighted[color][event.line_no - 1]
        else:
            self.c = NoColors()

            def highlighted(code):
                return code

            def highlighted_source_line(event):
                return event.source_line

        self.highlighted = highlighted
        self.highlighted_source_line = highlighted_source_line

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
        return short_filename(event.code)

    def full_file_column(self, event):
        return _get_filename(event)

    def function_column(self, event):
        return event.code.co_name

    def function_qualname_column(self, event):
        return event.code_qualname()

    def full_prefix(self, event):
        return u'{c.grey}{self.prefix}{indent}{columns} {c.reset}'.format(
            c=self.c,
            self=self,
            indent=event.depth * u'    ',
            columns=self.columns_string(event),
        )

    def format(self, event):
        # type: (Event) -> str
        lines = []

        if event.event in ('call', 'enter'):
            lines += self.format_start(event)

        statements = event.source.statements
        this_statement = statements[event.line_no]
        last_statement = statements[event.last_line_no]
        statement_start_lines = self.get_statement_start_lines(event, this_statement, last_statement)

        if event.event != 'exception':
            lines += self.format_variables(event, last_statement)

        if event.event == 'return':
            if not event.frame_info.is_ipython_cell:
                lines += self.format_return(event)
        elif event.event == 'exception':
            lines += self.format_exception(event)
        elif event.event == 'enter':
            pass
        elif event.event == 'exit':
            lines += [u'{c.green}<<< Exit with block in {func}{c.reset}'.format(
                c=self.c,
                func=event.code_qualname(),
            )]
        else:
            if not (
                    event.comprehension_type and event.event == 'line' or
                    event.frame_info.is_ipython_cell and event.event == 'call'
            ):
                lines += statement_start_lines + [self.format_event(event)]

        return self.format_lines(event, lines)

    def format_exception(self, event):
        lines = []
        exception_string = u''.join(traceback.format_exception_only(*event.arg[:2]))
        lines += [
            u'{c.red}!!! {line}{c.reset}'.format(
                c=self.c,
                line=line,
            )
            for line in exception_string.splitlines()
        ]
        lines += self.format_executing_node_exception(event)
        return lines

    def format_return(self, event):
        # If a call ends due to an exception, we still get a 'return' event
        # with arg = None. This seems to be the only way to tell the difference
        # https://stackoverflow.com/a/12800909/2482744
        opname = event.opname
        arg = event.arg
        if arg is None:
            if opname == 'END_FINALLY':
                if event.frame_info.had_exception:
                    return [u'{c.red}??? Call either returned None or ended by exception{c.reset}'
                                .format(c=self.c)]
            elif opname not in ('RETURN_VALUE', 'YIELD_VALUE'):
                return [u'{c.red}!!! Call ended by exception{c.reset}'.format(c=self.c)]

        value = self.highlighted(my_cheap_repr(arg))
        if event.comprehension_type:
            prefix = plain_prefix = u'Result: '
        else:
            plain_prefix = u'<<< {description} value from {func}: '.format(
                description='Yield' if opname == 'YIELD_VALUE' else 'Return',
                func=event.code_qualname(),
            )
            prefix = u'{c.green}{}{c.reset}'.format(
                plain_prefix,
                c=self.c,
            )
        return indented_lines(prefix, value, plain_prefix=plain_prefix)

    def get_statement_start_lines(self, event, this_statement, last_statement):
        result = []
        if (
                event.event != 'call' and
                this_statement and last_statement and
                this_statement != last_statement and
                this_statement.lineno != event.line_no and
                not isinstance(this_statement, try_statement)
        ):
            original_line_no = event.line_no
            for n in range(this_statement.lineno, original_line_no):
                event.line_no = n
                result.append(self.format_event(event))
            event.line_no = original_line_no
        return result

    def format_variables(self, event, last_statement):
        if last_statement:
            last_source_line = event.source.lines[last_statement.lineno - 1]
            dots = (get_leading_spaces(last_source_line)
                    .replace(' ', '.')
                    .replace('\t', '....'))
        else:
            dots = ''
            last_source_line = ''
        lines = []
        for var in event.variables:
            if (u'{} = {}'.format(*var) != last_source_line.strip()
                    and not (
                            isinstance(last_statement, ast.FunctionDef)
                            and not last_statement.decorator_list
                            and var[0] == last_statement.name
                    )
            ):
                lines += self.format_variable(var, dots, event.comprehension_type)
        return lines

    def format_start(self, event):
        if event.frame_info.is_ipython_cell:
            return []
        if event.comprehension_type:
            return [u'{type}:'.format(type=event.comprehension_type)]
        else:
            if event.event == 'enter':
                description = 'Enter with block in'
            else:
                assert event.event == 'call'
                if event.frame_info.is_generator:
                    if event.is_yield_value:
                        description = 'Re-enter generator'
                    else:
                        description = 'Start generator'
                else:
                    description = 'Call to'
            return [
                u'{c.cyan}>>> {description} {name} in File "{filename}", line {lineno}{c.reset}'.format(
                    name=event.code_qualname(),
                    filename=_get_filename(event),
                    lineno=event.line_no,
                    c=self.c,
                    description=description,
                )]

    def format_executing_node_exception(self, event):
        try:
            assert not NO_ASTTOKENS
            ex = Source.executing(event.frame)
            decorator = getattr(ex, "decorator", None)
            node = decorator or ex.node
            assert node

            description = {
                ast.Call: 'calling',
                ast.Subscript: 'subscripting',
                ast.Attribute: 'getting attribute',
                ast.Compare: 'comparing',
            }.get(type(node), 'evaluating')
            source = event.source.get_text_with_indentation(node)
            if decorator:
                description = 'calling decorator'
                source = '@' + source
            plain_prefix = u'!!! When {}: '.format(description)
            prefix = u'{c.red}{}{c.reset}'.format(plain_prefix, c=self.c)
            return indented_lines(
                prefix,
                source,
                plain_prefix=plain_prefix
            )
        except Exception:
            return []

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
        return u'{c.grey}{line_no:4}{c.reset} | {source_line}'.format(
            source_line=self.highlighted_source_line(entry),
            c=self.c,
            **entry.__dict__
        )

    def format_variable(self, entry, dots, is_comprehension):
        name, value = entry
        if name.startswith('.') and name[1:].isdigit():
            description = u'Iterating over'
        elif is_comprehension:
            description = u'Values of {name}:'.format(name=name)
        else:
            description = u'{name} ='.format(name=name)
        prefix = u'......{dots} {description} '.format(
            description=description,
            dots=dots,
        )
        return indented_lines(prefix, self.highlighted(value))

    def format_line_only(self, event):
        return self.format_lines(event, [self.format_event(event)])

    def format_log(self, event):
        return self.format_lines(event, ['LOG:'])

    def format_log_value(self, event, source, value, depth):
        prefix = u'....{} '.format(depth * 4 * '.')
        plain_source_lines = indented_lines(prefix, source)
        highl_source_lines = indented_lines(prefix, self.highlighted(source))

        plain_prefix = plain_source_lines[-1] + ' = '
        highl_prefix = highl_source_lines[-1] + ' = '

        lines = highl_source_lines[:-1] + indented_lines(
            highl_prefix,
            self.highlighted(value),
            plain_prefix=plain_prefix
        )
        return self.format_lines(event, lines)

    def format_lines(self, event, lines):
        prefix = self.full_prefix(event)
        return u''.join([
            (
                    prefix
                    + line
                    + u'\n'
            )
            for line in lines
        ])


def get_leading_spaces(s):
    return s[:len(s) - len(s.lstrip())]


def _get_filename(event):
    # return "/path/to/example.py"
    return event.code.co_filename


class NoColors(object):
    def __getattr__(self, item):
        return ''


class Colors(object):
    grey = '\x1b[90m'
    red = '\x1b[31m\x1b[1m'
    green = '\x1b[32m\x1b[1m'
    cyan = '\x1b[36m\x1b[1m'
    reset = '\x1b[0m'


def indented_lines(prefix, string, plain_prefix=None):
    lines = six.text_type(string).splitlines() or ['']
    return [prefix + lines[0]] + [
        u' ' * len(plain_prefix or prefix) + line
        for line in lines[1:]
    ]
