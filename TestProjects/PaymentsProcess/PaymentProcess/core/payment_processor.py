"""High-level orchestration for PaymentEvent processing.

The :class:`PaymentProcessor` coordinates Dry Run and Final Run workflows. Each
method intentionally delegates to specialized collaborators so individual
components remain testable and replaceable.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Protocol

from ..common.functions import get_default_workers
from ..data.config.config_loader import ConfigLoader
from ..data.models.event import PaymentEvent, RunMode
from ..data.models.stats import Finding, PaymentEventStats, ValidationReport
from ..data.repositories.claim_repository import ClaimRepository
from ..data.repositories.payment_center_repo import PaymentCenterRepository
from ..data.repositories.payment_repository import PaymentRepository


@dataclass(slots=True)
class RunSettings:
    """Immutable collection of runtime configuration for a processing cycle."""

    db_uri: str
    workers: int
    batch_size: int
    log_level: str


@dataclass(slots=True)
class Repositories:
    """Bundle of repository dependencies required by the processor."""

    claim_repo: ClaimRepository
    payment_repo: PaymentRepository
    payment_center_repo: PaymentCenterRepository


class ConnectionFactory(Protocol):
    """Protocol describing the minimal interface of a datastore connection."""

    def __call__(self, /) -> Any:  # pragma: no cover - protocol definition only
        ...


class PaymentProcessor:
    """Orchestrate the Dry Run and Final Run workflows.

    Parameters
    ----------
    config_loader:
        Loader responsible for retrieving and validating configuration entities.
    repositories:
        Data-access bundle used throughout the run.
    settings:
        Runtime configuration derived from CLI flags or environment defaults.
    """

    def __init__(
        self,
        config_loader: ConfigLoader,
        repositories: Repositories,
        settings: RunSettings,
    ) -> None:
        self._config_loader: ConfigLoader = config_loader
        self._repositories: Repositories = repositories
        self._settings: RunSettings = settings

    @classmethod
    def from_connection(cls, connection: Any, cli_args: Any) -> "PaymentProcessor":
        """Factory that wires repositories using a shared datastore connection.

        Replace the placeholder implementation once concrete repository
        classes accept actual driver clients. Keeping wiring logic here reduces
        duplication between CLI entry points and integration tests.
        """

        config_loader = ConfigLoader(connection)
        repositories = Repositories(
            claim_repo=ClaimRepository(connection),
            payment_repo=PaymentRepository(connection),
            payment_center_repo=PaymentCenterRepository(connection),
        )

        requested_workers = getattr(cli_args, "workers", None)
        workers = requested_workers if requested_workers else get_default_workers()
        batch_size = getattr(cli_args, "batch_size", None) or 1000

        settings = RunSettings(
            db_uri=getattr(cli_args, "db_uri", ""),
            workers=workers,
            batch_size=batch_size,
            log_level=getattr(cli_args, "log_level", "INFO"),
        )

        return cls(config_loader=config_loader, repositories=repositories, settings=settings)

    # Public API -----------------------------------------------------------------
    def run_dry_run(self, payment_event_id: str) -> PaymentEventStats:
        """Execute the Dry Run (pre-run estimate) workflow.

        The canonical flow should:

        1. Bootstrap stats and config (clone PaymentEvent, initialize metrics).
        2. Prepare PaymentCenters and working-set collections.
        3. Fetch/transform claims from ``ClaimWSCore`` and attach O/U context.
        4. Run estimate calculations at the claim level.
        5. Aggregate validation findings and finalize stats for QA review.

        Decompose each phase into dedicated helpers so the orchestration reads
        as a descriptive sequence of high-level operations.
        """

        stats: PaymentEventStats = self.initialize_stats(payment_event_id, RunMode.DRY_RUN.value)
        payment_event: PaymentEvent = self.load_config(payment_event_id)
        payment_event.run_mode = RunMode.DRY_RUN

        report: ValidationReport = self.validate_initial(payment_event, RunMode.DRY_RUN)
        if report.blocked:
            return self.finalize_stats(stats, report)

        center_summary = self.process_payment_centers(payment_event, ensure_create=False)
        claims = list(self.transform_claims(payment_event))
        self._apply_claim_metrics(stats, claims, center_summary)

        return self.finalize_stats(stats, report)

    def run_final_run(self, payment_event_id: str) -> PaymentEventStats:
        """Execute the Final Run (production) workflow.

        Expected phases:

        1. Load configuration from production collections and validate.
        2. Back up critical collections and refresh reference datasets.
        3. Create/align PaymentCenters, claim transforms, and O/U staging.
        4. Process service-line payments, roll up to claims, and persist.
        5. Re-run critical validations, update stats, and emit final totals.
        """

        stats: PaymentEventStats = self.initialize_stats(payment_event_id, RunMode.FINAL.value)
        payment_event: PaymentEvent = self.load_config(payment_event_id)
        payment_event.run_mode = RunMode.FINAL

        self._safe_backup()
        report: ValidationReport = self.validate_initial(payment_event, RunMode.FINAL)
        if report.blocked:
            return self.finalize_stats(stats, report)

        center_summary = self.process_payment_centers(payment_event, ensure_create=True)
        claims = list(self.transform_claims(payment_event))
        self._apply_claim_metrics(stats, claims, center_summary)

        return self.finalize_stats(stats, report)

    # Helper methods -------------------------------------------------------------
    def initialize_stats(self, payment_event_id: str, stage: str) -> PaymentEventStats:
        """Create or load the :class:`PaymentEventStats` record for this run.

        Capture timestamps and default totals here so downstream steps can
        append findings and metrics without worrying about initialization.
        """

        return PaymentEventStats(
            payment_event_id=payment_event_id,
            stage=stage,
            total_claims=0,
            started_at=self.now_utc(),
        )

    def load_config(self, payment_event_id: str) -> PaymentEvent:
        """Load primary configuration objects for the specified event.

        Delegate to :class:`ConfigLoader` and keep this method focused on
        orchestrating the sequence of loader calls and validations.
        """

        try:
            payment_event: PaymentEvent = self._config_loader.load_payment_event(payment_event_id, self._settings.db_uri)
        except NotImplementedError:
            payment_event = PaymentEvent(
                payment_event_id=payment_event_id,
                business_id="SAMPLE-BUSINESS",
                inclusion_criteria_id="INC-001",
                funding_source_id="FS-001",
                due_date=self.now_utc().date(),
                event_type="SAMPLE",
                stage="ready",
                run_mode=RunMode.DRY_RUN,
            )
        else:
            for loader in (
                self._config_loader.load_interest_config,
                self._config_loader.load_funding_source,
                self._config_loader.load_inclusion_criteria,
            ):
                try:
                    loader(payment_event, self._settings.db_uri)
                except NotImplementedError:
                    continue
            try:
                self._config_loader.validate(payment_event)
            except NotImplementedError:
                pass

        return payment_event

    def validate_initial(self, payment_event: PaymentEvent, mode: RunMode) -> ValidationReport:
        """Run initial validations and return a report for further handling.

        Let :class:`Validation` produce granular findings and convert them into
        a summary report that the orchestrator can interpret for control-flow
        decisions (e.g., abort on critical errors).
        """

        findings: list[Finding] = []

        if not payment_event.allowed_plans:
            findings.append(
                Finding(
                    severity="WARNING",
                    message="No benefit plans configured; using default sample scope.",
                    count=1,
                )
            )

        stage_name = (payment_event.stage or "").lower()
        blocked = mode == RunMode.FINAL and stage_name not in {"ready", "final"}
        if blocked:
            findings.append(
                Finding(
                    severity="CRITICAL",
                    message="Final run requires PaymentEvent.stage to be 'ready'.",
                    count=1,
                )
            )

        return ValidationReport(findings=findings, blocked=blocked)

    def now_utc(self) -> datetime:
        """Return the current UTC timestamp.

        Override or monkeypatch in tests to achieve deterministic outputs.
        """

        return datetime.utcnow()

    # Additional helper stubs ----------------------------------------------------
    def process_payment_centers(self, payment_event: PaymentEvent, ensure_create: bool) -> Any:
        """Placeholder for PaymentCenter processing logic.

        Expect this method to orchestrate PaymentCenter discovery, WS sync,
        optional production creation, and cache building. Return whatever
        summary structure downstream stages require.
        """

        center_types = payment_event.allowed_payment_center_types or ["GENERAL"]
        centers = [
            {
                "payment_center_id": idx,
                "center_type": center_type,
                "created": ensure_create,
            }
            for idx, center_type in enumerate(center_types, start=1)
        ]

        return {
            "centers": centers,
            "ensure_create": ensure_create,
        }

    def transform_claims(self, payment_event: PaymentEvent) -> Iterable[Any]:
        """Placeholder for claim retrieval and transformation step.

        Fetch raw claims, transform to ``PaymentCenterClaims`` structures, and
        attach over/under context so subsequent processors can run in isolation.
        """

        plans = payment_event.allowed_plans or ["PLAN-SAMPLE"]
        base_amount = 100.0 if payment_event.run_mode == RunMode.DRY_RUN else 150.0

        for idx, plan in enumerate(plans, start=1):
            projected_payment = base_amount + (idx - 1) * 10.0
            yield {
                "claim_id": f"{payment_event.payment_event_id}-{idx}",
                "benefit_plan_id": plan,
                "projected_payment": projected_payment,
                "payment_center_hint": idx,
            }

    def finalize_stats(self, stats: PaymentEventStats, report: ValidationReport) -> PaymentEventStats:
        """Finalize statistics before persisting results.

        Update timestamps, aggregate totals, and persist results to
        ``PaymentEventStats`` in a single place to avoid divergence across run
        modes.
        """

        stats.findings = report
        stats.completed_at = self.now_utc()

        if not stats.totals.by_payment_center:
            stats.totals.by_payment_center = {}
            stats.totals.overall = 0.0

        return stats

    # Internal helpers ---------------------------------------------------------
    def _apply_claim_metrics(
        self,
        stats: PaymentEventStats,
        claims: list[dict[str, Any]],
        center_summary: Any,
    ) -> None:
        """Populate totals and counts based on sample claim data."""

        centers = center_summary.get("centers", []) if isinstance(center_summary, dict) else []
        if not centers:
            centers = [{"payment_center_id": 0}]

        center_ids = [center["payment_center_id"] for center in centers]
        totals = {center_id: 0.0 for center_id in center_ids}

        for idx, claim in enumerate(claims):
            amount = float(claim.get("projected_payment", 0.0))
            hint = claim.get("payment_center_hint")
            center_id = hint if hint in totals else center_ids[idx % len(center_ids)]
            totals[center_id] += amount

        stats.total_claims = len(claims)
        stats.totals.by_payment_center = totals
        stats.totals.overall = sum(totals.values())

    def _safe_backup(self) -> None:
        """Best-effort backup invocation so sample flows mimic production steps."""

        try:
            self._repositories.claim_repo.backup(self._settings.db_uri)
        except (NotImplementedError, AttributeError):
            pass
