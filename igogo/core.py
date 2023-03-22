import asyncio
import functools
import inspect
import sys
from typing import Dict, List

import IPython
import greenback

from .context import IgogoContext, get_context_or_fail, set_context
from .output import OutputText, OutputStreamsSetter, OutputObject, OutputTextStyled
from .exceptions import IgogoInvalidContext, IgogoAdditionalOutputsExhausted

_igogo_run_loop = asyncio.get_running_loop()
_all_tasks: Dict[int, List[asyncio.Task]] = dict()
_igogo_count = 0


def _get_currently_running_cells_info():
    global _all_tasks
    keys = map(str, _all_tasks.keys())
    keys = '], ['.join(list(keys))
    if len(keys) > 0:
        keys = '[' + keys + ']'
    return keys


def _log_error(*argc, **kwargs):
    if not 'file' in kwargs:
        kwargs['file'] = sys.stderr
    print('[ IGOGO ]', *argc, **kwargs)
    running_s = _get_currently_running_cells_info()
    if len(running_s) == 0:
        running_s = '<none>'
    print(f'[ IGOGO ] Currently running IGOGO cells: {running_s}', file=kwargs['file'])


def stop():
    value = get_context_or_fail()
    value.task.cancel()


def get_running_igogo_cells():
    global _all_tasks
    _update_all_tasks()
    return list(_all_tasks.keys())


def sleep(delay, result=None):
    if not greenback.has_portal():
        raise IgogoInvalidContext()
    greenback.await_(asyncio.sleep(delay, result))


def display(object):
    value = get_context_or_fail()
    if len(value.additional_outputs) == 0:
        raise IgogoAdditionalOutputsExhausted()
    out = value.additional_outputs.pop()
    out.add_object(object)
    value.additional_outputs.insert(0, out)


def clear_output(including_text=True):
    value = get_context_or_fail()
    if including_text:
        value.out_stream.stdout.clear()
    for out in value.additional_outputs:
        out.clear()


def _update_all_tasks():
    global _all_tasks

    def filter_rule(task: asyncio.Task):
        return not task.done()

    for key in _all_tasks:
        _all_tasks[key] = list(filter(filter_rule, _all_tasks[key]))
    _all_tasks = {k: v for k, v in _all_tasks.items() if len(v) > 0}


def get_pending_tasks():
    return list(filter(lambda x: 'igogo' in x.get_name(), asyncio.all_tasks(loop=_igogo_run_loop)))


def stop_all():
    for task in get_pending_tasks():
        task.cancel()


def stop_latest():
    global _all_tasks
    _update_all_tasks()
    keys = list(_all_tasks.keys())
    if len(keys) == 0:
        _log_error("No running tasks")
        return
    latest_key = max(keys)
    task = _all_tasks[latest_key].pop()
    task.cancel()


def stop_by_cell_id(cell_id):
    global _all_tasks
    _update_all_tasks()

    cell_id = int(cell_id)
    if not cell_id in _all_tasks:
        _log_error(f"There's no running tasks in cell [{cell_id}]")
        return
    for task in _all_tasks[cell_id]:
        task.cancel()


def job(original_function=None, kind='stdout', displays=10):
    global _igogo_count

    def _decorate(function):
        @functools.wraps(function)
        def wrapped_function(*args, **kwargs):
            global _igogo_count, _all_tasks
            output_stream = OutputStreamsSetter(stdout=OutputText(kind=kind), stderr=OutputText(kind='stderr'))
            additional_outputs = list(reversed([OutputObject() for _ in range(displays)]))

            async def func_context_setter():
                await greenback.ensure_portal()
                set_context(
                    IgogoContext(task, output_stream, additional_outputs)
                )
                output_stream.activate()
                if inspect.iscoroutinefunction(function):
                    return await function(*args, **kwargs)
                return function(*args, **kwargs)

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

            ip = IPython.get_ipython()
            _all_tasks.setdefault(ip.execution_count, [])
            _all_tasks[ip.execution_count].append(task)

            return dict(
                task=task
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
