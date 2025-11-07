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
from ..data.models.stats import PaymentEventStats, ValidationReport
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
        self._config_loader = config_loader
        self._repositories = repositories
        self._settings = settings

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

        raise NotImplementedError("Dry Run workflow not yet implemented.")

    def run_final_run(self, payment_event_id: str) -> PaymentEventStats:
        """Execute the Final Run (production) workflow.

        Expected phases:

        1. Load configuration from production collections and validate.
        2. Back up critical collections and refresh reference datasets.
        3. Create/align PaymentCenters, claim transforms, and O/U staging.
        4. Process service-line payments, roll up to claims, and persist.
        5. Re-run critical validations, update stats, and emit final totals.
        """

        raise NotImplementedError("Final Run workflow not yet implemented.")

    # Helper methods -------------------------------------------------------------
    def initialize_stats(self, payment_event_id: str, stage: str) -> PaymentEventStats:
        """Create or load the :class:`PaymentEventStats` record for this run.

        Capture timestamps and default totals here so downstream steps can
        append findings and metrics without worrying about initialization.
        """

        raise NotImplementedError

    def load_config(self, payment_event_id: str) -> PaymentEvent:
        """Load primary configuration objects for the specified event.

        Delegate to :class:`ConfigLoader` and keep this method focused on
        orchestrating the sequence of loader calls and validations.
        """

        raise NotImplementedError

    def validate_initial(self, payment_event: PaymentEvent, mode: RunMode) -> ValidationReport:
        """Run initial validations and return a report for further handling.

        Let :class:`Validation` produce granular findings and convert them into
        a summary report that the orchestrator can interpret for control-flow
        decisions (e.g., abort on critical errors).
        """

        raise NotImplementedError

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

        raise NotImplementedError

    def transform_claims(self, payment_event: PaymentEvent) -> Iterable[Any]:
        """Placeholder for claim retrieval and transformation step.

        Fetch raw claims, transform to ``PaymentCenterClaims`` structures, and
        attach over/under context so subsequent processors can run in isolation.
        """

        raise NotImplementedError

    def finalize_stats(self, stats: PaymentEventStats, report: ValidationReport) -> PaymentEventStats:
        """Finalize statistics before persisting results.

        Update timestamps, aggregate totals, and persist results to
        ``PaymentEventStats`` in a single place to avoid divergence across run
        modes.
        """

        raise NotImplementedError
