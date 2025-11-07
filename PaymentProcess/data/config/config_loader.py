"""Configuration loading utilities for PaymentProcess."""

from __future__ import annotations

from typing import Any

from ..models.event import FundingSource, InclusionCriteria, InterestRules, PaymentEvent


class ConfigLoader:
    """Load PaymentEvent configuration data from the datastore."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def load_payment_event(self, payment_event_id: str, db_uri: str) -> PaymentEvent:
        """Load the :class:`PaymentEvent` entity."""

        raise NotImplementedError

    def load_interest_config(self, payment_event: PaymentEvent, db_uri: str) -> InterestRules:
        """Load interest configuration for the given PaymentEvent."""

        raise NotImplementedError

    def load_funding_source(self, payment_event: PaymentEvent, db_uri: str) -> FundingSource:
        """Load funding source configuration."""

        raise NotImplementedError

    def load_inclusion_criteria(self, payment_event: PaymentEvent, db_uri: str) -> InclusionCriteria:
        """Load inclusion criteria for the PaymentEvent."""

        raise NotImplementedError

    def validate(self, payment_event: PaymentEvent) -> None:
        """Perform configuration validation checks."""

        raise NotImplementedError
