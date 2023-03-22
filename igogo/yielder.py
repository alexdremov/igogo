from .core import get_context_or_fail
from .exceptions import IgogoInvalidContext

import greenback


class Yielder:

    @classmethod
    def igogo_await(cls):
        if not greenback.has_portal():
            raise IgogoInvalidContext()
        greenback.await_(cls())

    def __await__(self):
        try:
            value = get_context_or_fail()
        except IgogoInvalidContext:
            return
        yield
        value.out_stream.activate()
