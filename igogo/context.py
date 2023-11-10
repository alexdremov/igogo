#  Copyright (c) 2023.
#  Aleksandr Dremov

import asyncio
import contextvars
from typing import Optional, List

from .output import OutputStreamsSetter, OutputObject, AdditionalOutputs
from .exceptions import IgogoInvalidContext


class IgogoContext(object):
    """
    This class represents the context for running a function decorated by igogo job.
    """
    out_stream: OutputStreamsSetter
    task: asyncio.Task
    additional_outputs: AdditionalOutputs

    def __init__(
            self,
            task: asyncio.Task,
            out_stream: OutputStreamsSetter,
            additional_outputs: AdditionalOutputs
    ):
        self.out_stream = out_stream
        self.task = task
        self.additional_outputs = additional_outputs

        out_stream.register_activate_callback(additional_outputs.after_context_enter)
        out_stream.register_deactivate_callback(additional_outputs.before_context_exit)


_context: contextvars.ContextVar[Optional[IgogoContext]] = contextvars.ContextVar("igogo_context", default=None)


def get_context_or_none() -> IgogoContext:
    return _context.get()


def get_context_or_fail() -> IgogoContext:
    value = get_context_or_none()
    if value is None:
        raise IgogoInvalidContext()
    return value


def set_context(context: IgogoContext):
    _context.set(context)
