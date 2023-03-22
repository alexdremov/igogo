import IPython
from IPython.core.magic import (Magics, magics_class, cell_magic)

@magics_class
class IgogoMagic(Magics):
    @cell_magic
    def igogo(self, line, cell):
        ip = IPython.get_ipython()
        args: dict = eval(f"dict({line})")
        args.setdefault('update_globals', False)
        update_globals = args['update_globals']
        args.pop('update_globals')
        prefix = "def __igogo_magic_wrapper():\n" \
                 "    import igogo\n" \
                 f"    @igogo.job(**dict({args}))\n" \
                 "    async def execute():\n"\
                 "        global " + ', '.join(list(IPython.get_ipython().user_ns.keys())) + '\n'
        cell = prefix + '\n'.join(['        ' + line for line in cell.split('\n')])
        cell += "\n" + \
               ("        globals().update(locals())\n" if update_globals else "") + \
                "    return execute()\n" \
                "__igogo_magic_wrapper()"
        ip.run_cell(cell, silent=True)

