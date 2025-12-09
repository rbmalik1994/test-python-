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

        self._rules_loaded = True
        base_amount = service_line.allowed_amount * service_line.quantity
        adjustment = context.settings.get("adjustment_factor", 1.0)
        calculated_amount = round(base_amount * adjustment, 2)
        previous_balance = max(context.over_under.previous_balance, 0.0)
        offsets = min(previous_balance, calculated_amount * 0.5)
        payment = ServiceLinePayment(
            service_line=service_line,
            calculated_amount=calculated_amount,
            offsets_applied=round(offsets, 2),
            metadata={
                "payment_event_id": payment_event.payment_event_id,
                "source": context.payment_event_id,
            },
        )
        return payment

    def rollup_to_claim(self, parent_group: ParentGroup) -> ClaimPayment:
        """Aggregate service-line payments into claim-level totals."""

        service_line_payments: list[ServiceLinePayment] = []
        total = 0.0
        candidates = parent_group.paid_claims + parent_group.adjust_claims
        if not candidates:
            candidates = parent_group.void_claims
        for claim in candidates:
            for sl in claim.service_lines:
                line = ServiceLine(
                    service_code=sl.service_code,
                    charge_amount=sl.billed_amount,
                    allowed_amount=sl.allowed_amount,
                    quantity=1.0,
                )
                payment = ServiceLinePayment(
                    service_line=line,
                    calculated_amount=sl.allowed_amount,
                    offsets_applied=0.0,
                    metadata={"claim_id": claim.claim_id},
                )
                service_line_payments.append(payment)
                total += sl.allowed_amount
        return ClaimPayment(
            claim_id=parent_group.parent_id,
            service_line_payments=service_line_payments,
            total_amount=round(total, 2),
        )

    def apply_interest(
        self,
        claim_payment: ClaimPayment,
        rules: InterestRules,
        due_date: date,
    ) -> ClaimPayment:
        """Apply interest calculations to a claim payment."""

        days_late = max((date.today() - due_date).days - rules.grace_period_days, 0)
        interest = round(claim_payment.total_amount * rules.rate * days_late / 365, 2)
        claim_payment.interest_amount = interest
        claim_payment.total_amount = round(claim_payment.total_amount + interest, 2)
        return claim_payment
