"""Process-based parallelism helpers."""

from __future__ import annotations

from typing import Callable, Iterable, List, Sequence, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def run_pc_level(tasks: Iterable[T], fn: Callable[[T], R], workers: int) -> List[R]:
    """Execute PaymentCenter-level tasks in parallel."""

    raise NotImplementedError


def run_claim_batch_level(batches: Iterable[Sequence[T]], fn: Callable[[Sequence[T]], R], workers: int) -> List[R]:
    """Execute claim batch-level tasks in parallel."""

    raise NotImplementedError


def run_service_line_level(batches: Iterable[Sequence[T]], fn: Callable[[Sequence[T]], R], workers: int) -> List[R]:
    """Execute service-line level tasks in parallel."""

    raise NotImplementedError
