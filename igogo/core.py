import asyncio
import functools

from .context import IgogoContext, get_context_or_fail, set_context
from .output import Output, OutputStream

_igogo_run_loop = asyncio.get_running_loop()


def stop():
    value = get_context_or_fail()
    value.task.cancel()


def job(original_function=None, kind='text'):
    def _decorate(function):
        @functools.wraps(function)
        def wrapped_function(*args, **kwargs):
            output_stream = OutputStream(Output(kind=kind))
            output_stream.activate()

            async def func_context_setter():
                set_context(
                    IgogoContext(task, output_stream)
                )
                await function(*args, **kwargs)

            coro = func_context_setter()

            if not hasattr(wrapped_function, "tasks"):
                wrapped_function.tasks = []

            task = _igogo_run_loop.create_task(coro)
            wrapped_function.tasks.append(task)

            def done_callback(t):
                try:
                    exception = task.exception()
                    if exception is not None:
                        raise exception
                except asyncio.CancelledError:
                    pass

            task.add_done_callback(done_callback)

            return task

        def stopall():
            for task in wrapped_function.tasks:
                task.cancel()

        from .yielder import Yielder
        wrapped_function.yielder = Yielder
        wrapped_function.stopall = stopall
        wrapped_function.stop = stop
        return wrapped_function

    if original_function:
        return _decorate(original_function)
    return _decorate
