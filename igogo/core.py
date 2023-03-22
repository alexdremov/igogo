import asyncio
import functools
import greenback

from .context import IgogoContext, get_context_or_fail, set_context
from .output import Output, OutputStream
from .exceptions import IgogoInvalidContext

_igogo_run_loop = asyncio.get_running_loop()
_igogo_count = 0


def stop():
    value = get_context_or_fail()
    value.task.cancel()


def sleep(delay, result=None):
    if not greenback.has_portal():
        raise IgogoInvalidContext()
    greenback.await_(asyncio.sleep(delay, result))


def run():
    def get_pending():
        return list(filter(lambda x: 'igogo' in x.get_name(), asyncio.all_tasks(loop=_igogo_run_loop)))

    pending_all = get_pending()
    while len(pending_all):
        pending = pending_all[-1]
        _igogo_run_loop.run_until_complete(pending)
        pending_all = get_pending()


def job(original_function=None, kind='text'):
    global _igogo_count

    def _decorate(function):
        @functools.wraps(function)
        def wrapped_function(*args, **kwargs):
            global _igogo_count
            output_stream = OutputStream(Output(kind=kind))
            output_stream.activate()

            async def func_context_setter():
                await greenback.ensure_portal()
                set_context(
                    IgogoContext(task, output_stream)
                )
                output_stream.activate()
                return await function(*args, **kwargs)

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
            task.set_name(f'igogo_{_igogo_count}')
            _igogo_count += 1

            return dict(
                task=task,
                output=output_stream.out
            )

        def stop_all():
            if not hasattr(wrapped_function, "tasks"):
                wrapped_function.tasks = []
            for task in wrapped_function.tasks:
                task.cancel()

        from .yielder import Yielder
        wrapped_function.yielder = Yielder
        wrapped_function.stop_all = stop_all
        wrapped_function.stop = stop
        return wrapped_function

    if original_function:
        return _decorate(original_function)
    return _decorate
