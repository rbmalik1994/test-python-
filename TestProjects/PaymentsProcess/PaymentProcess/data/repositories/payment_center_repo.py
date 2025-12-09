"""Repository for PaymentCenter operations."""

from __future__ import annotations

from typing import Any, Iterable, List

from ..models.payment_center import PaymentCenterCache


class PaymentCenterRepository:
    """Manage PaymentCenter persistence and retrieval."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection
        self._ws_storage: dict[int, dict[str, Any]] = {}
        self._prod_storage: dict[int, dict[str, Any]] = {}
        self._key_index: dict[str, int] = {}
        self._next_id: int = 1
        self._last_backup: str | None = None

    def copy_to_ws(self, payment_center_ids: Iterable[int], db_uri: str) -> None:
        """Copy PaymentCenters to the working-set collection."""

        for center_id in payment_center_ids:
            record = self._prod_storage.get(center_id, {"payment_center_id": center_id, "source": "prod"})
            self._ws_storage[center_id] = dict(record)

    def create_ws(self, missing_keys: Iterable[str], db_uri: str) -> list[int]:
        """Create missing PaymentCenters in the working-set collection."""

        created_ids: List[int] = []
        for key in missing_keys:
            if not key:
                continue
            if key in self._key_index:
                created_ids.append(self._key_index[key])
                continue
            center_id = self._next_id
            self._next_id += 1
            self._key_index[key] = center_id
            self._ws_storage[center_id] = {"payment_center_id": center_id, "composite_key": key, "source": "ws"}
            created_ids.append(center_id)
        return created_ids

    def create_prod_if_missing(self, ws_created: Iterable[int], db_uri: str) -> list[int]:
        """Create production PaymentCenters when missing."""

        promoted: List[int] = []
        for center_id in ws_created:
            if center_id not in self._prod_storage and center_id in self._ws_storage:
                self._prod_storage[center_id] = dict(self._ws_storage[center_id], source="prod")
            promoted.append(center_id)
        return promoted

    def get_cache(self, keys: Iterable[str], db_uri: str) -> PaymentCenterCache:
        """Build an in-memory cache for PaymentCenter lookups."""

        cache: PaymentCenterCache = {}
        for key in keys:
            if key not in self._key_index:
                center_id = self._next_id
                self._next_id += 1
                self._key_index[key] = center_id
                self._ws_storage.setdefault(center_id, {"payment_center_id": center_id, "composite_key": key, "source": "ws"})
            cache[key] = self._key_index[key]
        return cache

    def backup(self, db_uri: str) -> str:
        """Create a backup of PaymentCenter collections."""

        self._last_backup = f"payment-centers-backup::{db_uri}"
        return self._last_backup
