"""Thread-based parallelism helpers."""

from __future__ import annotations

from typing import Callable, Iterable, List, Sequence, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def thread_map(fn: Callable[[T], R], items: Iterable[T], workers: int) -> List[R]:
    """Execute a function across items using a thread pool."""

    raise NotImplementedError


def thread_batch(fn: Callable[[Sequence[T]], R], batches: Iterable[Sequence[T]], workers: int) -> List[R]:
    """Execute a batch function using threads."""

    raise NotImplementedError
