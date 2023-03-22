from .context import get_context_or_none, get_context_or_fail
from .exceptions import IgogoInvalidContext

import greenback


class Yielder:

    @classmethod
    def igogo_await(cls):
        if not greenback.has_portal() and get_context_or_none() is None:
            return
        elif not greenback.has_portal():
            raise IgogoInvalidContext()
        greenback.await_(cls())
        value = get_context_or_fail()
        value.out_stream.activate()

    def __await__(self):
        try:
            get_context_or_fail()
        except IgogoInvalidContext:
            return
        yield
        value = get_context_or_fail()
        value.out_stream.activate()
