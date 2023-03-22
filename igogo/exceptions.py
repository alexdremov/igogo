import io
class IgogoInvalidContext(Exception):
    def __init__(self):
        from .core import _log_error
        file = io.StringIO()
        _log_error('Igogo command invoked from invalid context', file=file)
        super().__init__(file.getvalue())
        file.close()


class IgogoAdditionalOutputsExhausted(Exception):
    def __init__(self):
        from .core import _log_error
        file = io.StringIO()
        _log_error('Igogo invoked display function, but cell has not enough display capabilities', file=file)
        super().__init__(file.getvalue())
        file.close()
