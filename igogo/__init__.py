import IPython
from .yielder import Yielder as yielder
from .core import job, stop
from .loaders import register_hooks as _register_hooks
from .loaders import IpythonWatcher
from .loaders import load_ipython_extension

_ip = IPython.get_ipython()
_watcher = IpythonWatcher(_ip)
_register_hooks(_watcher, _ip)
