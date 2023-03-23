#  Copyright (c) 2023.
#  Aleksandr Dremov

from .context import get_context_or_none, get_context_or_fail
from .exceptions import IgogoInvalidContext

import greenback


class Yielder:
    """
    A class that provides methods for yielding igogo job execution
    """

    @classmethod
    def igogo_await(cls):
        """
        This method that suspends the execution of igogo job, allowing other jobs to run.

        If `greenback` does not have a portal and the current context does not
        exist, this method returns immediately without doing anything.

        If `greenback` does not have a portal, it raises `IgogoInvalidContext`.

        If there are no running igogo jobs, this method returns immediately
        without doing anything.

        Otherwise, this method awaits and activates the output stream.
        """
        if not greenback.has_portal() and get_context_or_none() is None:
            return
        elif not greenback.has_portal():
            raise IgogoInvalidContext()
        from igogo import get_running_igogo_cells
        if len(get_running_igogo_cells()) == 0:
            return
        value = get_context_or_fail()
        value.out_stream.deactivate()
        greenback.await_(cls())
        value.out_stream.activate()

    def __await__(self):
        """
        If the current context does not exist, this method returns immediately
        without doing anything.

        Otherwise, this method suspends execution.
        """
        yield
