"""Validation routines for PaymentProcess workflows.

The :class:`Validation` class groups related checks so they can be reused across
Dry Run and Final Run flows. Each method should focus on a single validation
concern and return lightweight results that can be aggregated into a
:class:`~PaymentProcess.data.models.stats.ValidationReport`.
"""

from __future__ import annotations

from typing import Iterable, List

from ..data.models.claim import Claim, ClaimStatus, FrequencyCode
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

    def _capture(self, finding: Finding) -> Finding:
        self._findings.append(finding)
        return finding

    def _coerce_claims(self, claims: Iterable[Claim]) -> list[Claim]:
        return claims if isinstance(claims, list) else list(claims)

    def validate_frequency_codes(self, claims: Iterable[Claim]) -> Finding:
        """Ensure claims use allowed frequency codes."""

        claims_list = self._coerce_claims(claims)
        invalid = [claim.claim_id for claim in claims_list if claim.frequency_code not in FrequencyCode]
        severity = "INFO" if not invalid else "WARNING"
        message = "All frequency codes valid" if not invalid else "Claims contain unsupported frequency codes"
        finding = Finding(severity=severity, message=message, count=len(invalid), sample_ids=invalid[:5])
        return self._capture(finding)

    def validate_identifiers(self, claims: Iterable[Claim], pc_type: PaymentCenterType) -> Finding:
        """Verify identifiers (TIN, NPI, Member ID) based on PaymentCenter type."""

        claims_list = self._coerce_claims(claims)
        missing = []
        for claim in claims_list:
            if pc_type == PaymentCenterType.PROVIDER and not (claim.tin or claim.npi):
                missing.append(claim.claim_id)
            elif pc_type == PaymentCenterType.DMR and not claim.member_id:
                missing.append(claim.claim_id)
        severity = "INFO" if not missing else "WARNING"
        message = "Identifiers present for all claims" if not missing else "Missing identifiers for PaymentCenter type"
        finding = Finding(severity=severity, message=message, count=len(missing), sample_ids=missing[:5])
        return self._capture(finding)

    def validate_duplicates(self, claims: Iterable[Claim]) -> Finding:
        """Detect duplicate claim records."""

        claims_list = self._coerce_claims(claims)
        seen: set[str] = set()
        duplicates: list[str] = []
        for claim in claims_list:
            if claim.claim_id in seen:
                duplicates.append(claim.claim_id)
            else:
                seen.add(claim.claim_id)
        severity = "INFO" if not duplicates else "CRITICAL"
        message = "No duplicate claims detected" if not duplicates else "Duplicate claim identifiers detected"
        finding = Finding(severity=severity, message=message, count=len(duplicates), sample_ids=duplicates[:5])
        return self._capture(finding)

    def validate_negative_dollars(self, claims: Iterable[Claim]) -> Finding:
        """Identify claims with negative financial amounts."""

        claims_list = self._coerce_claims(claims)
        offending = []
        for claim in claims_list:
            for sl in claim.service_lines:
                if sl.allowed_amount < 0 or sl.billed_amount < 0:
                    offending.append(claim.claim_id)
                    break
        severity = "INFO" if not offending else "WARNING"
        message = "No negative dollar amounts" if not offending else "Negative dollar amounts detected"
        finding = Finding(severity=severity, message=message, count=len(offending), sample_ids=offending[:5])
        return self._capture(finding)

    def validate_missing_parent_paid(self, claims: Iterable[Claim]) -> Finding:
        """Check for missing parent claim payment references."""

        claims_list = self._coerce_claims(claims)
        missing = []
        for claim in claims_list:
            if not claim.parent_claim_core_id and claim.status == ClaimStatus.CLOSED:
                missing.append(claim.claim_id)
        severity = "INFO" if not missing else "WARNING"
        message = "All paid claims linked to a parent" if not missing else "Paid claims missing parent references"
        finding = Finding(severity=severity, message=message, count=len(missing), sample_ids=missing[:5])
        return self._capture(finding)

    def validate_benefit_plan(self, claims: Iterable[Claim], plans: set[str]) -> Finding:
        """Validate benefit plan membership for claims."""

        claims_list = self._coerce_claims(claims)
        invalid = [claim.claim_id for claim in claims_list if claim.benefit_plan_id and claim.benefit_plan_id not in plans]
        severity = "INFO" if not invalid else "WARNING"
        message = "All claims within allowed plans" if not invalid else "Claims found outside allowed plans"
        finding = Finding(severity=severity, message=message, count=len(invalid), sample_ids=invalid[:5])
        return self._capture(finding)

    def validate_void_linkages(self, claims: Iterable[Claim]) -> Finding:
        """Validate void and adjustment linkages."""

        claims_list = self._coerce_claims(claims)
        invalid = [claim.claim_id for claim in claims_list if claim.frequency_code == FrequencyCode.VOID and not claim.parent_claim_core_id]
        severity = "INFO" if not invalid else "WARNING"
        message = "Void linkages valid" if not invalid else "Void claims missing parent linkage"
        finding = Finding(severity=severity, message=message, count=len(invalid), sample_ids=invalid[:5])
        return self._capture(finding)

    def validate_payment_centers(self, summary: PaymentCenterSummary) -> Finding:
        """Validate PaymentCenter summary data."""

        severity = "INFO"
        message = "PaymentCenter summary healthy"
        sample: list[str] = []
        count = 0
        if summary.missing_keys:
            severity = "CRITICAL"
            message = "Missing PaymentCenters detected"
            sample = summary.missing_keys[:5]
            count = len(summary.missing_keys)
        elif summary.created_prod_ids:
            severity = "INFO"
            message = "PaymentCenters created during sync"
            count = len(summary.created_prod_ids)
        finding = Finding(severity=severity, message=message, count=count, sample_ids=sample)
        return self._capture(finding)

    def validate_sequences(self, report: SequenceReport) -> Finding:
        """Validate sequence number usage for the run."""

        discrepancies = []
        for key, expected in report.expected.items():
            actual = report.actual.get(key)
            if actual != expected:
                discrepancies.append(f"{key}:{actual}->{expected}")
        severity = "INFO" if not discrepancies else "WARNING"
        message = "Sequences verified" if not discrepancies else "Sequence allocation mismatch"
        finding = Finding(severity=severity, message=message, count=len(discrepancies), sample_ids=discrepancies[:5])
        return self._capture(finding)

    def aggregate_findings(self, findings: List[Finding]) -> ValidationReport:
        """Aggregate findings into a report for downstream consumption."""

        combined = self._findings + findings
        blocked = any(is_critical(finding) for finding in combined)
        report = ValidationReport(findings=combined, blocked=blocked)
        return report


def is_critical(finding: Finding) -> bool:
    """Return ``True`` if a finding should block the run."""

    return finding.severity.upper() == "CRITICAL"


def raise_if_blocking(report: ValidationReport, mode: str) -> None:
    """Raise an exception if a validation report contains blocking findings."""

    if report.blocked:
        messages = "; ".join(f"{finding.message} ({finding.count})" for finding in report.findings if is_critical(finding))
        raise RuntimeError(f"{mode} run blocked: {messages}")
