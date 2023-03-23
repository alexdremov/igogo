#  Copyright (c) 2023.
#  Aleksandr Dremov

import IPython.display, sys


class IpythonWatcher(object):
    def __init__(self, ip, stdout, stderr):
        self.shell = ip
        self.init_stdout = stdout
        self.init_stderr = stderr

    def _exchange_stdouts(self):
        sys.stdout, self.init_stdout = self.init_stdout, sys.stdout
        sys.stderr, self.init_stderr = self.init_stderr, sys.stderr

    def _activate_prev_outputs(self):
        ...

    def pre_execute(self):
        self._exchange_stdouts()

    def pre_run_cell(self, info):
        ...

    def post_execute(self):
        self._exchange_stdouts()

    def post_run_cell(self, result):
        ...


def register_hooks(watcher: IpythonWatcher, ip):
    ...
    # ip.events.register("pre_execute", watcher.pre_execute)
    # ip.events.register("pre_run_cell", watcher.pre_run_cell)
    # ip.events.register("post_execute", watcher.post_execute)
    # ip.events.register("post_run_cell", watcher.post_run_cell)


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    from .magic import IgogoMagic
    ipython.register_magics(IgogoMagic)

def _modify_styles():
    IPython.display.display_html(IPython.display.HTML("""
    <style>
        div.output_text { padding: 0; }
        div.output_text pre:empty { padding: 0; }
    </style>
    """))
