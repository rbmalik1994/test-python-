"""Process-based parallelism helpers."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from typing import Callable, Iterable, List, Sequence, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def run_pc_level(tasks: Iterable[T], fn: Callable[[T], R], workers: int) -> List[R]:
    """Execute PaymentCenter-level tasks in parallel."""

    return _execute_parallel(tasks, fn, workers)


def run_claim_batch_level(batches: Iterable[Sequence[T]], fn: Callable[[Sequence[T]], R], workers: int) -> List[R]:
    """Execute claim batch-level tasks in parallel."""

    return _execute_parallel(batches, fn, workers)


def run_service_line_level(batches: Iterable[Sequence[T]], fn: Callable[[Sequence[T]], R], workers: int) -> List[R]:
    """Execute service-line level tasks in parallel."""

    return _execute_parallel(batches, fn, workers)


def _execute_parallel(items: Iterable[T], fn: Callable[[T], R], workers: int) -> List[R]:
    items_list = list(items)
    if not items_list:
        return []
    worker_count = max(1, workers)
    try:
        with ProcessPoolExecutor(max_workers=worker_count) as executor:
            return [result for result in executor.map(fn, items_list)]
    except Exception:
        # Fall back to synchronous execution for functions that cannot be pickled.
        return [fn(item) for item in items_list]
