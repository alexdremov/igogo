import IPython
from IPython.core.magic import (Magics, magics_class, cell_magic)

@magics_class
class IgogoMagic(Magics):
    @cell_magic
    def igogo(self, line, cell):
        ip = IPython.get_ipython()
        prefix = "def __igogo_magic_wrapper():\n    import igogo\n    @igogo.job\n    async def execute():\n"
        cell = prefix + '\n'.join(['        ' + line for line in cell.split('\n')])
        cell += "    execute()\n__igogo_magic_wrapper()"
        ip.run_cell(cell)
        return None
