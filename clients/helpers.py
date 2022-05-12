from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

def now_ts() -> int:
  return int(datetime.utcnow().timestamp()) * 1000


def run_io_tasks_in_parallel(tasks: list[Callable]):
  with ThreadPoolExecutor() as executor:
    running_tasks = [executor.submit(task) for task in tasks]
    for running_task in running_tasks:
      running_task.result()
