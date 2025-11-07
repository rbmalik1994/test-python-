"""Repository handling payment persistence."""

from __future__ import annotations

from typing import Any, Iterable

from ..models.over_under import OverUnderRecord
from ..models.payment import ClaimPayment, ServiceLinePayment


class PaymentRepository:
    """Persist calculated payment data to the datastore."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def persist_service_line(self, payment: ServiceLinePayment, db_uri: str) -> None:
        """Persist service-line payment output.

        Callers should use :meth:`ServiceLinePayment.model_dump` when writing
        back to MongoDB to ensure consistent serialization.
        """

        raise NotImplementedError

    def persist_claim_aggregate(self, payment: ClaimPayment, db_uri: str) -> None:
        """Persist claim-level payment aggregates.

        Use :meth:`ClaimPayment.model_dump` for converting the model back to a
        Mongo-ready document.
        """

        raise NotImplementedError

    def calc_and_upsert_over_under(
        self,
        payment_event_id: str,
        payment_center_id: int,
        records: Iterable[OverUnderRecord],
        db_uri: str,
    ) -> None:
        """Calculate summaries and upsert over/under payment records."""

        raise NotImplementedError

    def backup(self, db_uri: str) -> str:
        """Create a backup of payment-related collections."""

        raise NotImplementedError
