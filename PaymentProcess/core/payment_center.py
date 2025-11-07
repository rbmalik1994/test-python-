"""PaymentCenter lifecycle management utilities."""

from __future__ import annotations

from typing import Iterable, Set

from ..data.models.claim import Claim
from ..data.models.payment_center import (
    PaymentCenterCache,
    PaymentCenterSummary,
    PaymentCenterType,
)


class PaymentCenterManager:
    """Handle PaymentCenter discovery, synchronization, and caching."""

    def __init__(self) -> None:
        self._cache: PaymentCenterCache = {}

    def derive_unique_keys(self, claims: Iterable[Claim], pc_type: PaymentCenterType) -> Set[str]:
        """Derive unique PaymentCenter keys from claim data."""

        raise NotImplementedError

    def sync_to_ws(self, keys: Set[str]) -> PaymentCenterSummary:
        """Synchronize PaymentCenters into the working-set collection."""

        raise NotImplementedError

    def create_missing_in_prod(self, summary: PaymentCenterSummary) -> dict[str, int]:
        """Create missing PaymentCenters in production and return identifiers."""

        raise NotImplementedError

    def build_cache(self, summary: PaymentCenterSummary) -> PaymentCenterCache:
        """Construct an in-memory cache mapping composite keys to IDs."""

        raise NotImplementedError
