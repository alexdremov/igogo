from typing import List
import asyncio
import contextvars

from .output import OutputStreamsSetter, OutputObject
from .exceptions import IgogoInvalidContext


class IgogoContext(object):
    out_stream: OutputStreamsSetter
    task: asyncio.Task
    additional_outputs: List[OutputObject]

    def __init__(self, task: asyncio.Task, out_stream: OutputStreamsSetter, additional_outputs: List[OutputObject]):
        self.out_stream = out_stream
        self.task = task
        self.additional_outputs = additional_outputs


_context: contextvars.ContextVar[IgogoContext | None] = contextvars.ContextVar("igogo_context", default=None)


def get_context_or_none() -> IgogoContext:
    return _context.get()


def get_context_or_fail() -> IgogoContext:
    value = get_context_or_none()
    if value is None:
        raise IgogoInvalidContext()
    return value


def set_context(context: IgogoContext):
    _context.set(context)
