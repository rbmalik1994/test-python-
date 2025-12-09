"""Configuration loading utilities for PaymentProcess."""

from __future__ import annotations

from datetime import date
from typing import Any, Mapping

from ..models.event import FundingSource, InclusionCriteria, InterestRules, PaymentEvent, RunMode


class ConfigLoader:
    """Load PaymentEvent configuration data from the datastore."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    # ------------------------------------------------------------------
    def _lookup(self, bucket: str, key: str) -> dict[str, Any] | None:
        """Retrieve a record from the optional connection mapping."""

        if isinstance(self._connection, Mapping):
            bucket_data = self._connection.get(bucket, {})
            if isinstance(bucket_data, Mapping):
                record = bucket_data.get(key)
                if isinstance(record, Mapping):
                    return dict(record)
        return None

    def load_payment_event(self, payment_event_id: str, db_uri: str) -> PaymentEvent:
        """Load the :class:`PaymentEvent` entity."""

        record = self._lookup("payment_events", payment_event_id)
        if not record:
            record = {
                "payment_event_id": payment_event_id,
                "business_id": "DEMO-BIZ",
                "inclusion_criteria_id": "INC-DEFAULT",
                "funding_source_id": "FUND-DEFAULT",
                "due_date": date.today(),
                "event_type": "SAMPLE",
                "stage": "ready",
                "run_mode": RunMode.DRY_RUN,
                "allowed_plans": ["PLAN-A", "PLAN-B"],
                "allowed_payment_center_types": ["PROVIDER"],
            }
        payment_event = PaymentEvent.model_validate(record)
        setattr(payment_event, "db_uri", db_uri)
        return payment_event

    def load_interest_config(self, payment_event: PaymentEvent, db_uri: str) -> InterestRules:
        """Load interest configuration for the given PaymentEvent."""

        rules = self._lookup("interest_rules", payment_event.payment_event_id)
        if not rules:
            rules = {"rate": 0.05, "grace_period_days": 30}
        interest_rules = InterestRules.model_validate(rules)
        setattr(payment_event, "interest_rules", interest_rules)
        return interest_rules

    def load_funding_source(self, payment_event: PaymentEvent, db_uri: str) -> FundingSource:
        """Load funding source configuration."""

        record = self._lookup("funding_sources", payment_event.funding_source_id)
        if not record:
            record = {
                "account_number": "000-FAKE",
                "description": f"Sample funding for {payment_event.payment_event_id}",
            }
        funding_source = FundingSource.model_validate(record)
        setattr(payment_event, "funding_source", funding_source)
        return funding_source

    def load_inclusion_criteria(self, payment_event: PaymentEvent, db_uri: str) -> InclusionCriteria:
        """Load inclusion criteria for the PaymentEvent."""

        record = self._lookup("inclusion_criteria", payment_event.inclusion_criteria_id)
        if not record:
            record = {
                "allowed_benefit_plans": set(payment_event.allowed_plans or ["PLAN-A"]),
                "allowed_payment_centers": set(range(1, 4)),
            }
        inclusion = InclusionCriteria.model_validate(record)
        if inclusion.allowed_benefit_plans:
            payment_event.allowed_plans = sorted(inclusion.allowed_benefit_plans)
        if inclusion.allowed_payment_centers:
            setattr(payment_event, "allowed_payment_centers", sorted(inclusion.allowed_payment_centers))
        return inclusion

    def validate(self, payment_event: PaymentEvent) -> None:
        """Perform configuration validation checks."""

        errors: list[str] = []
        if not payment_event.allowed_plans:
            errors.append("PaymentEvent must specify at least one allowed plan.")
        if payment_event.due_date < date.today():
            errors.append("PaymentEvent due date cannot be in the past for sample runs.")
        if errors:
            joined = " ".join(errors)
            raise ValueError(joined)
