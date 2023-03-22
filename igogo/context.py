from .output import OutputStream
import asyncio
import contextvars
from .exceptions import IgogoInvalidContext


class IgogoContext(object):
    out_stream: OutputStream
    task: asyncio.Task

    def __init__(self, task: asyncio.Task, out_stream: OutputStream):
        self.out_stream = out_stream
        self.task = task


_context: contextvars.ContextVar[IgogoContext | None] = contextvars.ContextVar("igogo_context", default=None)


def get_context_or_fail() -> IgogoContext:
    value = _context.get()
    if value is None:
        raise IgogoInvalidContext()
    return value

def set_context(context: IgogoContext):
    _context.set(context)
