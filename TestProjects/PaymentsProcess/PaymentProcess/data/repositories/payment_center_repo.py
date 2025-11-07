"""Repository for PaymentCenter operations."""

from __future__ import annotations

from typing import Any, Iterable

from ..models.payment_center import PaymentCenterCache


class PaymentCenterRepository:
    """Manage PaymentCenter persistence and retrieval."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def copy_to_ws(self, payment_center_ids: Iterable[int], db_uri: str) -> None:
        """Copy PaymentCenters to the working-set collection."""

        raise NotImplementedError

    def create_ws(self, missing_keys: Iterable[str], db_uri: str) -> list[int]:
        """Create missing PaymentCenters in the working-set collection."""

        raise NotImplementedError

    def create_prod_if_missing(self, ws_created: Iterable[int], db_uri: str) -> list[int]:
        """Create production PaymentCenters when missing."""

        raise NotImplementedError

    def get_cache(self, keys: Iterable[str], db_uri: str) -> PaymentCenterCache:
        """Build an in-memory cache for PaymentCenter lookups."""

        raise NotImplementedError

    def backup(self, db_uri: str) -> str:
        """Create a backup of PaymentCenter collections."""

        raise NotImplementedError
