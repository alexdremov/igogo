#  Copyright (c) 2023.
#  Aleksandr Dremov

import IPython
import sys
from .yielder import Yielder as yielder_async
from .core import job, stop, sleep, display, clear_output, stop_all
from .core import stop_by_cell_id, stop_latest, get_running_igogo_cells
from .loaders import register_hooks as _register_hooks
from .loaders import IpythonWatcher
from .loaders import load_ipython_extension, _modify_styles

_ip = IPython.get_ipython()
_watcher = IpythonWatcher(_ip, sys.stdout, sys.stderr)
_register_hooks(_watcher, _ip)
_modify_styles()

yielder = yielder_async.igogo_await
