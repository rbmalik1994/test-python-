"""Thread-based parallelism helpers."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable, List, Sequence, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def thread_map(fn: Callable[[T], R], items: Iterable[T], workers: int) -> List[R]:
    """Execute a function across items using a thread pool."""

    items_list = list(items)
    if not items_list:
        return []
    worker_count = max(1, workers)
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        return list(executor.map(fn, items_list))


def thread_batch(fn: Callable[[Sequence[T]], R], batches: Iterable[Sequence[T]], workers: int) -> List[R]:
    """Execute a batch function using threads."""

    batches_list = list(batches)
    if not batches_list:
        return []
    worker_count = max(1, workers)
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        return list(executor.map(fn, batches_list))
