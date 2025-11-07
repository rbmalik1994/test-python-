"""Batching utilities used throughout PaymentProcess."""

from __future__ import annotations

from typing import Iterable, Iterator, List, Sequence, TypeVar

T = TypeVar("T")


def batch_iterable(items: Iterable[T], size: int) -> Iterator[List[T]]:
    """Yield lists of ``size`` from ``items`` until exhausted."""

    raise NotImplementedError


def bulk_upsert(collection: str, documents: Sequence[dict], ordered: bool = False) -> dict:
    """Perform a bulk upsert into the datastore."""

    raise NotImplementedError


def allocate_sequence_chunks(name: str, chunk_size: int, workers: int) -> List[int]:
    """Allocate sequence number chunks for worker consumption."""

    raise NotImplementedError
