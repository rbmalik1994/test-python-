"""Validation routines for PaymentProcess workflows.

The :class:`Validation` class groups related checks so they can be reused across
Dry Run and Final Run flows. Each method should focus on a single validation
concern and return lightweight results that can be aggregated into a
:class:`~PaymentProcess.data.models.stats.ValidationReport`.
"""

from __future__ import annotations

from typing import Iterable, List

from ..data.models.claim import Claim
from ..data.models.payment_center import PaymentCenterSummary, PaymentCenterType
from ..data.models.stats import Finding, SequenceReport, ValidationReport


class Validation:
    """Collection of validation helpers.

    Inject collaborators (logging, configuration) via the constructor when the
    real implementation is added. Keeping the constructor optional makes early
    unit testing easier.
    """

    def __init__(self) -> None:
        self._findings: list[Finding] = []

    def validate_frequency_codes(self, claims: Iterable[Claim]) -> Finding:
        """Ensure claims use allowed frequency codes."""

        raise NotImplementedError

    def validate_identifiers(self, claims: Iterable[Claim], pc_type: PaymentCenterType) -> Finding:
        """Verify identifiers (TIN, NPI, Member ID) based on PaymentCenter type."""

        raise NotImplementedError

    def validate_duplicates(self, claims: Iterable[Claim]) -> Finding:
        """Detect duplicate claim records."""

        raise NotImplementedError

    def validate_negative_dollars(self, claims: Iterable[Claim]) -> Finding:
        """Identify claims with negative financial amounts."""

        raise NotImplementedError

    def validate_missing_parent_paid(self, claims: Iterable[Claim]) -> Finding:
        """Check for missing parent claim payment references."""

        raise NotImplementedError

    def validate_benefit_plan(self, claims: Iterable[Claim], plans: set[str]) -> Finding:
        """Validate benefit plan membership for claims."""

        raise NotImplementedError

    def validate_void_linkages(self, claims: Iterable[Claim]) -> Finding:
        """Validate void and adjustment linkages."""

        raise NotImplementedError

    def validate_payment_centers(self, summary: PaymentCenterSummary) -> Finding:
        """Validate PaymentCenter summary data."""

        raise NotImplementedError

    def validate_sequences(self, report: SequenceReport) -> Finding:
        """Validate sequence number usage for the run."""

        raise NotImplementedError

    def aggregate_findings(self, findings: List[Finding]) -> ValidationReport:
        """Aggregate findings into a report for downstream consumption."""

        raise NotImplementedError


def is_critical(finding: Finding) -> bool:
    """Return ``True`` if a finding should block the run."""

    return finding.severity.upper() == "CRITICAL"


def raise_if_blocking(report: ValidationReport, mode: str) -> None:
    """Raise an exception if a validation report contains blocking findings."""

    raise NotImplementedError
