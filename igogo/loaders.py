from ipykernel.zmqshell import ZMQInteractiveShell
from .output import OutputStream, Output


class IpythonWatcher(object):
    def __init__(self, ip: ZMQInteractiveShell):
        self.shell = ip

    def pre_execute(self):
        stream = OutputStream(Output())
        stream.activate()

    def pre_run_cell(self, info):
        ...

    def post_execute(self):
        ...

    def post_run_cell(self, result):
        ...


def register_hooks(watcher: IpythonWatcher, ip: ZMQInteractiveShell):
    ip.events.register("pre_execute", watcher.pre_execute)
    ip.events.register("pre_run_cell", watcher.pre_run_cell)
    ip.events.register("post_execute", watcher.post_execute)
    ip.events.register("post_run_cell", watcher.post_run_cell)


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    from .magic import IgogoMagic
    ipython.register_magics(IgogoMagic)
