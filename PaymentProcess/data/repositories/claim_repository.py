"""Repository for claim-related datastore operations."""

from __future__ import annotations

from typing import Any, Iterable, List

from ..models.claim import Claim


class ClaimRepository:
    """Data access object for claims."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def fetch_ws(self, payment_event_id: str, db_uri: str, projection: dict | None = None) -> Iterable[Claim]:
        """Fetch claims from the working-set collection."""

        raise NotImplementedError

    def fetch_fin(self, payment_event_id: str, db_uri: str, projection: dict | None = None) -> Iterable[Claim]:
        """Fetch claims from the production collection."""

        raise NotImplementedError

    def backup(self, db_uri: str) -> str:
        """Create a backup of the relevant claim collection."""

        raise NotImplementedError

    def hydrate_claims(self, raw_records: Iterable[dict]) -> List[Claim]:
        """Convert raw MongoDB documents into validated :class:`Claim` models.

        The expectation for bulk pipelines is to load documents in one pass,
        coerce them via :meth:`Claim.model_validate`, and return models ready
        for processing by :class:`PaymentProcess.core.claim_processor.ClaimTransformer`.
        """

        raise NotImplementedError
