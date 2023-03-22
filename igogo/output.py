import random
import string
import io
import sys
from IPython import display


def is_lab_notebook():
    import re
    import psutil

    return any(re.search('jupyter-lab', x)
               for x in psutil.Process().parent().cmdline())

class Output:
    def __init__(self, kind='text', display_id=None):
        if display_id is None:
            self.display_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=100))
        else:
            self.display_id = display_id

        self.h = display.display(display_id=self.display_id)
        self.kind = kind
        self.content = ''
        self.mime_type = None
        self.dic_kind = {
            'text': 'text/plain',
            'markdown': 'text/markdown',
            'html': 'text/html',
        }
        if not is_lab_notebook():
            self.display()

    def display(self):
        self.h.display({'text/plain': ''}, raw=True)

    def _build_obj(self, content, kind, append, new_line):
        self.mime_type = self.dic_kind.get(kind)
        if not self.mime_type:
            return content, False
        if append:
            sep = '\n' if new_line else ''
            self.content = self.content + sep + content
        else:
            self.content = content
        if self.kind == 'markdown':
            self.content = self.content.replace('\n', '<br>')
        return {self.mime_type: self.content}, True

    def update(self, content, append=True, new_line=False):
        obj, raw = self._build_obj(content, self.kind, append, new_line)
        self.h.update(obj, raw=raw)


class OutputStream(io.IOBase):
    def __init__(self, out: Output):
        self.out = out

    def write(self, data):
        self.out.update(data)

    def flush(self):
        pass

    def activate(self):
        sys.stdout = self
        sys.stderr = self
