"""Service-line level payment computations."""

from __future__ import annotations

from datetime import date

from ..data.models.claim import ParentGroup
from ..data.models.event import InterestRules, PaymentEvent
from ..data.models.payment import ClaimPayment, PaymentContext, ServiceLine, ServiceLinePayment


class ServiceLineProcessor:
    """Compute service-line payments and aggregate to claims."""

    def __init__(self) -> None:
        self._rules_loaded = False

    def compute_service_line(
        self,
        service_line: ServiceLine,
        payment_event: PaymentEvent,
        context: PaymentContext,
    ) -> ServiceLinePayment:
        """Compute payment values for a single service line."""

        raise NotImplementedError

    def rollup_to_claim(self, parent_group: ParentGroup) -> ClaimPayment:
        """Aggregate service-line payments into claim-level totals."""

        raise NotImplementedError

    def apply_interest(
        self,
        claim_payment: ClaimPayment,
        rules: InterestRules,
        due_date: date,
    ) -> ClaimPayment:
        """Apply interest calculations to a claim payment."""

        raise NotImplementedError
