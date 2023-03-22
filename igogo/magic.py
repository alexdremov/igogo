import IPython
from IPython.core.magic import (Magics, magics_class, cell_magic)
from .output import Output

@magics_class
class IgogoMagic(Magics):
    @cell_magic
    def igogo(self, line, cell):
        ip = IPython.get_ipython()
        prefix = "def __igogo_magic_wrapper():\n" \
                 "    import igogo\n" \
                 f"    @igogo.job(**dict({line}))\n" \
                 "    async def execute():\n"
        cell = prefix + '\n'.join(['        ' + line for line in cell.split('\n')])
        cell += "\n" \
                "    return execute()\n" \
                "__igogo_magic_wrapper()"
        ip.ex(cell)
