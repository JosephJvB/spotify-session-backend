from datetime import datetime
from concurrent import futures
from typing import Callable

def now_ts() -> int:
  return int(datetime.utcnow().timestamp()) * 1000


def run_io_tasks_in_parallel(tasks: list[Callable]) -> list:
  with futures.ThreadPoolExecutor() as executor:
    parallel_tasks = [executor.submit(task) for task in tasks]
    futures.wait(parallel_tasks)
    return [t.result() for t in parallel_tasks]
