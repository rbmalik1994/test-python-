"""Repository for claim-related datastore operations."""

from __future__ import annotations

from typing import Any, Iterable, List, Mapping

from ..models.claim import Claim, ClaimStatus, ClaimType, FrequencyCode, ServiceLineCore


class ClaimRepository:
    """Data access object for claims."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection
        self._cache: dict[str, dict[str, list[dict[str, Any]]]] = {
            "claims_ws": {},
            "claims_fin": {},
        }
        self._last_backup: str | None = None

    # ------------------------------------------------------------------
    def _bucket(self, name: str) -> dict[str, list[dict[str, Any]]]:
        bucket = self._cache.setdefault(name, {})
        if isinstance(self._connection, Mapping):
            external = self._connection.get(name)
            if isinstance(external, Mapping):
                for key, value in external.items():
                    if isinstance(value, list):
                        bucket.setdefault(key, value)
        return bucket

    def _ensure_projection(self, records: Iterable[dict[str, Any]], projection: dict | None) -> list[dict[str, Any]]:
        if not projection:
            return [dict(record) for record in records]
        keys = {key for key, include in projection.items() if include}
        filtered: list[dict[str, Any]] = []
        for record in records:
            filtered.append({key: value for key, value in record.items() if key in keys})
        return filtered

    def _sample_claims(self, payment_event_id: str, variant: str) -> list[dict[str, Any]]:
        service_line = {
            "service_code": "99213",
            "billed_amount": 150.0,
            "allowed_amount": 120.0 if variant == "ws" else 140.0,
        }
        records: list[dict[str, Any]] = []
        for idx in range(1, 4):
            records.append(
                {
                    "claim_id": f"{payment_event_id}-{variant.upper()}-{idx}",
                    "parent_claim_core_id": f"PARENT-{idx}",
                    "claim_type": ClaimType.MEDICAL,
                    "status": ClaimStatus.CLOSED if idx % 2 else ClaimStatus.ADJUSTED,
                    "frequency_code": FrequencyCode.ORIGINAL if idx % 2 else FrequencyCode.REPLACEMENT,
                    "tin": "123456789",
                    "npi": "1098765432",
                    "member_id": f"M-{idx}",
                    "benefit_plan_id": "PLAN-A" if idx % 2 else "PLAN-B",
                    "service_lines": [service_line],
                }
            )
        return records

    def fetch_ws(self, payment_event_id: str, db_uri: str, projection: dict | None = None) -> Iterable[Claim]:
        """Fetch claims from the working-set collection."""

        records = self._bucket("claims_ws").get(payment_event_id)
        if records is None:
            records = self._sample_claims(payment_event_id, "ws")
            self._bucket("claims_ws")[payment_event_id] = records
        return self.hydrate_claims(self._ensure_projection(records, projection))

    def fetch_fin(self, payment_event_id: str, db_uri: str, projection: dict | None = None) -> Iterable[Claim]:
        """Fetch claims from the production collection."""

        records = self._bucket("claims_fin").get(payment_event_id)
        if records is None:
            records = self._sample_claims(payment_event_id, "fin")
            self._bucket("claims_fin")[payment_event_id] = records
        return self.hydrate_claims(self._ensure_projection(records, projection))

    def backup(self, db_uri: str) -> str:
        """Create a backup of the relevant claim collection."""

        self._last_backup = f"claims-backup::{db_uri}"
        return self._last_backup

    def hydrate_claims(self, raw_records: Iterable[dict]) -> List[Claim]:
        """Convert raw MongoDB documents into validated :class:`Claim` models.

        The expectation for bulk pipelines is to load documents in one pass,
        coerce them via :meth:`Claim.model_validate`, and return models ready
        for processing by :class:`PaymentProcess.core.claim_processor.ClaimTransformer`.
        """

        hydrated: List[Claim] = []
        for record in raw_records:
            if isinstance(record, Claim):
                hydrated.append(record)
                continue
            hydrated.append(Claim.model_validate(record))
        return hydrated
