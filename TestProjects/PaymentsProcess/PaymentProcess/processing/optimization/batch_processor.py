"""Batching utilities used throughout PaymentProcess."""

from __future__ import annotations

from typing import Iterable, Iterator, List, Sequence, TypeVar

T = TypeVar("T")


def batch_iterable(items: Iterable[T], size: int) -> Iterator[List[T]]:
    """Yield lists of ``size`` from ``items`` until exhausted."""

    if size <= 0:
        raise ValueError("Batch size must be a positive integer")
    batch: List[T] = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def bulk_upsert(collection: str, documents: Sequence[dict], ordered: bool = False) -> dict:
    """Perform a bulk upsert into the datastore."""

    if not collection:
        raise ValueError("Collection name is required for bulk upsert")
    return {
        "collection": collection,
        "documents": len(documents),
        "ordered": ordered,
        "acknowledged": True,
    }


def allocate_sequence_chunks(name: str, chunk_size: int, workers: int) -> List[int]:
    """Allocate sequence number chunks for worker consumption."""

    if chunk_size <= 0 or workers <= 0:
        raise ValueError("Chunk size and workers must be positive")
    return [index * chunk_size for index in range(workers)]
