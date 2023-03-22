import IPython
from .yielder import Yielder as yielder_async
from .core import job, stop, sleep, display, clear_output, stop_all
from .core import stop_by_cell_id, stop_latest, get_running_igogo_cells
from .loaders import register_hooks as _register_hooks
from .loaders import IpythonWatcher
from .loaders import load_ipython_extension

yielder = yielder_async.igogo_await

__igogo_inited = False

if not __igogo_inited:
    __igogo_inited = True
    _ip = IPython.get_ipython()
    _watcher = IpythonWatcher(_ip)
    _register_hooks(_watcher, _ip)
