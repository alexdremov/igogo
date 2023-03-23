#  Copyright (c) 2023.
#  Aleksandr Dremov

import random
import string
import io
import sys
from typing import List

from IPython import display
from IPython.core.interactiveshell import InteractiveShell


def is_lab_notebook():
    import re
    import psutil

    return any(re.search('jupyter-lab', x)
               for x in psutil.Process().parent().cmdline())


class OutputBase:
    def __init__(self, display_id=None):
        if display_id is None:
            self.display_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=100))
        else:
            self.display_id = display_id

        self.handle = display.display(display_id=self.display_id)
        self.metadata = dict()
        self.dic_kind = {
            'text': 'text/plain',
            'markdown': 'text/markdown',
            'html': 'text/html',
            'stderr': 'text/plain',
            'stdout': 'text/plain'
        }
        self.objs = [{'text/plain': ''}]
        if not is_lab_notebook():
            self.display()

    def display(self, update=False):
        display.display(
            *self.objs,
            display_id=self.display_id,
            update=update,
            raw=True,
            metadata=self.metadata,
            transient={
                'display_id': self.display_id
            }
        )

    def _build_obj(self, content, kind):
        mime_type = self.dic_kind.get(kind, kind)
        return {mime_type: content}

    def _update(self):
        self.display(update=True)

    def clear(self):
        self.text = ''
        self.objs = []
        self.metadata = dict()
        self._update()


class OutputText(OutputBase, io.IOBase):

    def __init__(self, kind, display_id=None):
        super().__init__(display_id)
        self.text = ''
        self.kind = kind

    def add_text(self, content):
        self.text += content
        self.objs = [self._build_obj(self.text, self.kind)]
        self._update()

    def flush(self): ...

    def write(self, data):
        self.add_text(data)


class OutputObject(OutputBase):
    def add_object(self, obj, include=None, exclude=None):
        fmt = InteractiveShell.instance().display_formatter.format
        format_dict, md_dict = fmt(obj, include=include, exclude=exclude)
        if not format_dict:
            return
        self.objs = [format_dict]
        self.metadata = md_dict
        self._update()


class OutputTextStyled(OutputBase, io.IOBase):
    def __init__(self, style_start='', style_end='', kind='html'):
        super().__init__()
        self.text = ''
        self.style_end = style_end
        self.style_start = style_start
        self.kind = kind

    def _build_styled(self, content):
        type = self.dic_kind.get(self.kind)
        content = self.style_start + content + self.style_end
        return {type: content}

    def add_text(self, content):
        self.text += content
        self.objs = [self._build_styled(self.text)]
        self._update()

    def write(self, data):
        self.add_text(data)

    def flush(self): ...


class OutputStreamsSetter:
    def __init__(self, stdout: OutputText, stderr: OutputText):
        self.stdout = stdout
        self.stderr = stderr
        self.activated = False

    def _exchange(self):
        self.stdout, sys.stdout = sys.stdout, self.stdout
        self.stderr, sys.stderr = sys.stderr, self.stderr

    def activate(self, force=False):
        if not self.activated or force:
            self._exchange()
            self.activated = True

    def deactivate(self, force=False):
        if self.activated or force:
            self._exchange()
            self.activated = False


class AdditionalOutputs:
    additional_outputs: List[OutputObject]
    counter: int
    no_warn: bool

    def __init__(self, count=1, no_warn=False):
        self.additional_outputs = [OutputObject() for _ in range(count)]
        self.counter = 0
        self.no_warn = no_warn

    def get_next(self):
        if self.counter == len(self.additional_outputs) and not self.no_warn:
            from .core import _log_warning
            _log_warning(f'Exhausted all {self.counter} displays. Will overwrite the oldest.')
        self.counter += 1
        return self.additional_outputs[(self.counter - 1) % len(self.additional_outputs)]

    def is_empty(self):
        return len(self.additional_outputs) == 0

    def clear(self):
        for disp in self.additional_outputs:
            disp.clear()
