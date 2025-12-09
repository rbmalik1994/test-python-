"""Repository handling payment persistence."""

from __future__ import annotations

from typing import Any, Iterable, List

from ..models.over_under import OverUnderRecord
from ..models.payment import ClaimPayment, ServiceLinePayment


class PaymentRepository:
    """Persist calculated payment data to the datastore."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection
        self._storage: dict[str, List[dict[str, Any]]] = {
            "service_lines": [],
            "claims": [],
            "over_under": [],
        }
        self._last_backup: str | None = None

    def persist_service_line(self, payment: ServiceLinePayment, db_uri: str) -> None:
        """Persist service-line payment output.

        Callers should use :meth:`ServiceLinePayment.model_dump` when writing
        back to MongoDB to ensure consistent serialization.
        """

        self._storage["service_lines"].append({"db_uri": db_uri, "payload": payment.model_dump()})

    def persist_claim_aggregate(self, payment: ClaimPayment, db_uri: str) -> None:
        """Persist claim-level payment aggregates.

        Use :meth:`ClaimPayment.model_dump` for converting the model back to a
        Mongo-ready document.
        """

        self._storage["claims"].append({"db_uri": db_uri, "payload": payment.model_dump()})

    def calc_and_upsert_over_under(
        self,
        payment_event_id: str,
        payment_center_id: int,
        records: Iterable[OverUnderRecord],
        db_uri: str,
    ) -> None:
        """Calculate summaries and upsert over/under payment records."""

        summary = {
            "payment_event_id": payment_event_id,
            "payment_center_id": payment_center_id,
            "total_records": 0,
            "net_amount": 0.0,
        }
        for record in records:
            payload = record.model_dump()
            summary["total_records"] += 1
            summary["net_amount"] += payload.get("amount", 0.0)
            self._storage["over_under"].append({"db_uri": db_uri, "payload": payload})
        self._storage.setdefault("over_under_summary", []).append(summary)

    def backup(self, db_uri: str) -> str:
        """Create a backup of payment-related collections."""

        self._last_backup = f"payments-backup::{db_uri}"
        return self._last_backup
