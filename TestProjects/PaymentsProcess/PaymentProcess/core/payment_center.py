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
        self._next_id: int = 1

    def derive_unique_keys(self, claims: Iterable[Claim], pc_type: PaymentCenterType) -> Set[str]:
        """Derive unique PaymentCenter keys from claim data."""

        keys: Set[str] = set()
        for claim in claims:
            if pc_type == PaymentCenterType.PROVIDER:
                identifier = claim.tin or claim.npi or claim.member_id or "UNKNOWN"
            else:
                identifier = claim.member_id or claim.benefit_plan_id or "UNKNOWN"
            keys.add(f"{pc_type.value}:{identifier}")
        return keys

    def sync_to_ws(self, keys: Set[str]) -> PaymentCenterSummary:
        """Synchronize PaymentCenters into the working-set collection."""

        summary = PaymentCenterSummary()
        for key in sorted(keys):
            if key in self._cache:
                summary.existing_ids.append(self._cache[key])
            else:
                summary.missing_keys.append(key)
        return summary

    def create_missing_in_prod(self, summary: PaymentCenterSummary) -> dict[str, int]:
        """Create missing PaymentCenters in production and return identifiers."""

        created: dict[str, int] = {}
        for key in summary.missing_keys:
            if key not in self._cache:
                self._cache[key] = self._next_id
                summary.created_ws_ids.append(self._next_id)
                summary.created_prod_ids.append(self._next_id)
                self._next_id += 1
            created[key] = self._cache[key]
        return created

    def build_cache(self, summary: PaymentCenterSummary) -> PaymentCenterCache:
        """Construct an in-memory cache mapping composite keys to IDs."""

        relevant_ids = set(summary.existing_ids + summary.created_ws_ids + summary.created_prod_ids)
        cache: PaymentCenterCache = {}
        for key, value in self._cache.items():
            if not relevant_ids or value in relevant_ids:
                cache[key] = value
        return cache
