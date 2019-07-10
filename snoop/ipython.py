import ast

from snoop import snoop
from IPython import get_ipython
from IPython.core.magic import Magics, cell_magic, magics_class


@magics_class
class SnoopMagics(Magics):
    @cell_magic
    def snoop(self, _line, cell):
        shell = get_ipython()
        filename = shell.compile.cache(cell)
        code = shell.compile(cell, filename, 'exec')
        tracer = snoop()

        tracer.variable_whitelist = set()
        for node in ast.walk(ast.parse(cell)):
            if isinstance(node, ast.Name):
                tracer.variable_whitelist.add(node.id)

        tracer.target_codes.add(code)
        with tracer:
            shell.ex(code)
