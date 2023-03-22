from .core import get_context_or_fail


class Yielder:
    def __await__(self):
        value = get_context_or_fail()
        yield
        value.out_stream.activate()
