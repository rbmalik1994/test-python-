# PaymentProcess structure and API design

This document defines the concrete folder and file structure for the PaymentProcess application, with detailed module responsibilities, exported symbols, classes, functions, custom variables, and CLI entry points. It is derived from `process_flow.md` and expands it into an implementable skeleton.


## High-level overview

- Purpose: Implement the end-to-end PaymentEvent processing (Dry Run and Final Run) with validations, PaymentCenter handling, Claim transformation, O/U lifecycle, and payment calculations.
- Design pillars:
  - Clear separation of concerns (core logic, data access, models, parallelism, utils)
  - Testability (unit for logic, integration for pipelines)
  - Performance via batching and multi-processing
  - Auditability via stats and structured logging


## Folder tree

```text
PaymentProcess/
├── core/
│   ├── payment_processor.py       # Orchestrates Dry Run and Final Run
│   ├── validation.py              # Validations and checks (critical/warn/info)
│   ├── payment_center.py          # PaymentCenter lifecycle and caching
│   ├── claim_processor.py         # Claim retrieval/transformation to PaymentCenterClaims
│   └── service_line_processor.py  # Final run service-line computations and rollups
├── data/
│   ├── models/                    # Data models (dataclasses/TypedDicts)
│   │   ├── claim.py               # Claim, Parent group, status/type enums
│   │   ├── payment.py             # Payment, offsets, interest
│   │   ├── payment_center.py      # PaymentCenter, keys, types
│   │   ├── over_under.py          # Over/Under lifecycle models
│   │   ├── event.py               # PaymentEvent, InclusionCriteria, FundingSource, Interest
│   │   └── stats.py               # PaymentEventStats shapes
│   ├── repositories/              # Data access layer (DB/collections)
│   │   ├── claim_repository.py    # ClaimWSCore/ClaimFinCore access
│   │   ├── payment_repository.py  # PaymentInfo persistence, O/U writes
│   │   └── payment_center_repo.py # PaymentCenter WS/prod management
│   └── config/
│       └── config_loader.py       # Load/validate run configuration
├── processing/
│   ├── parallel/
│   │   ├── multiprocessing.py     # Process pool helpers for PCs/claims/lines
│   │   └── multithreading.py      # Thread pool helpers for IO batching
│   └── optimization/
│       └── batch_processor.py     # Chunking, bulk ops, sequence allocation
├── docs/
│   ├── process_flow.md            # Process flow (source)
│   └── api_docs.md                # Generated/handwritten API docs (optional)
├── tests/
│   ├── unit/                      # Unit tests
│   ├── integration/               # End-to-end synthetic cycles
│   └── performance/               # Throughput/latency checks
├── utils/
│   ├── logging.py                 # Logging setup (JSON/structured)
│   └── error_handling.py          # Exceptions and error taxonomy
└── main.py                        # CLI entrypoint for runs
```


## Top-level files

### `main.py`
- Responsibility: CLI entrypoint that wires arguments to `PaymentProcessor`.
- Public functions:
  - `main(argv: list[str] | None = None) -> int`
    - Parses CLI args (via `argument.py`), configures logging, and dispatches to Dry Run or Final Run.
- Behavior:
  - Returns process exit code (0 success, non-zero on critical errors).

### `argument.py` (placed at project root alongside `main.py`)
- Responsibility: CLI argument parsing and validation.
- Public functions:
  - `build_arg_parser() -> argparse.ArgumentParser`
  - `parse_args(argv: list[str] | None = None) -> argparse.Namespace`
  - `validate_args(ns: argparse.Namespace) -> None`
- Key CLI options (recommended):
  - `--payment-event-id, -p` (str, required)
  - `--mode, -m` (choices: `dry-run`, `final`, required)
  - `--workers` (int, default: env/CPU-bound heuristic)
  - `--batch-size` (int, default 1000)
  - `--log-level` (str, default INFO)
  - `--config-path` (path to external config, optional)
  - `--db-uri` (override datastore connection, optional)
  - `--resume` (flag to resume a failed run where safe)
  - `--pc-type` (choices: `provider`, `dmr`, optional to override config)
  - `--validate-only` (flag to run validations without calculations)

### `__init__.py` files
- At `PaymentProcess/__init__.py`:
  - Purpose: Provide top-level API and version.
  - Exports (`__all__`): `PaymentProcessor`, `Validation`, `PaymentCenterManager`, `ClaimTransformer`, `ServiceLineProcessor`
  - Optional: `__version__ = "0.1.0"`
- At subpackages (`core`, `data`, `data/models`, `data/repositories`, `processing`, `processing/parallel`, `processing/optimization`, `utils`):
  - Purpose: Re-export commonly-used classes/functions for convenient imports.


## Module-by-module details

### `core/payment_processor.py`
- Class: `PaymentProcessor`
  - Purpose: Orchestrate Pre-Run (Dry Run) and Final Run.
  - Constructor:
    - `__init__(self, config_loader: ConfigLoader, repos: Repositories, settings: RunSettings)`
  - Methods:
    - `run_dry_run(self, payment_event_id: str) -> PaymentEventStats`
    - `run_final_run(self, payment_event_id: str) -> PaymentEventStats`
    - `initialize_stats(self, payment_event_id: str, stage: str) -> PaymentEventStats`
    - `load_config(self, payment_event_id: str) -> PaymentEvent`
    - `validate_initial(self, pe: PaymentEvent, mode: RunMode) -> ValidationReport`
    - `process_payment_centers(self, pe: PaymentEvent, source: ClaimSource, ensure_create: bool) -> PaymentCenterSummary`
    - `transform_claims(self, pe: PaymentEvent, source: ClaimSource) -> list[PaymentCenterClaims]`
    - `prepare_over_under(self, pe: PaymentEvent) -> None`
    - `estimate_claim_payments(self, pc_claims: list[PaymentCenterClaims], pe: PaymentEvent) -> EstimateResult`
    - `compute_service_line_payments(self, pc_claims: list[PaymentCenterClaims], pe: PaymentEvent) -> FinalRunResult`
    - `apply_over_under_offsets(self, final_result: FinalRunResult, pe: PaymentEvent) -> None`
    - `final_validations(self, report: ValidationReport, mode: RunMode) -> None`
    - `finalize_stats(self, stats: PaymentEventStats, findings: ValidationReport, totals: Totals) -> PaymentEventStats`

- Standalone helper functions (optional):
  - `now_utc() -> datetime`
  - `stage_label(mode: RunMode) -> str`

### `core/validation.py`
- Class: `Validation`
  - Methods (Critical/Warning/Info grouped):
    - `validate_frequency_codes(claims: Iterable[Claim]) -> Finding`
    - `validate_identifiers(claims: Iterable[Claim], pc_type: PaymentCenterType) -> Finding`
    - `validate_duplicates(claims: Iterable[Claim]) -> Finding`
    - `validate_negative_dollars(claims: Iterable[Claim]) -> Finding`
    - `validate_missing_parent_paid(claims: Iterable[Claim]) -> Finding`
    - `validate_benefit_plan(claims: Iterable[Claim], plans: set[str]) -> Finding`
    - `validate_void_linkages(claims: Iterable[Claim]) -> Finding`
    - `validate_payment_centers(pc_summary: PaymentCenterSummary) -> Finding`
    - `validate_sequences(seq_report: SequenceReport) -> Finding`
    - `aggregate_findings(findings: list[Finding]) -> ValidationReport`

- Standalone:
  - `is_critical(f: Finding) -> bool`
  - `raise_if_blocking(report: ValidationReport, mode: RunMode) -> None`

### `core/payment_center.py`
- Class: `PaymentCenterManager`
  - Methods:
    - `derive_unique_keys(claims: Iterable[Claim], pc_type: PaymentCenterType) -> set[str]`
    - `sync_to_ws(keys: set[str]) -> PaymentCenterSummary`  (copy OLD, create NEW in WS)
    - `create_missing_in_prod(summary: PaymentCenterSummary) -> CreatedReport`
    - `build_cache(summary: PaymentCenterSummary) -> PaymentCenterCache`

- Types:
  - `PaymentCenterCache = dict[str, int]` (key string -> PaymentCenter_ID)

### `core/claim_processor.py`
- Class: `ClaimTransformer`
  - Methods:
    - `fetch_claims(self, source: ClaimSource, pe: PaymentEvent) -> Iterable[Claim]`
    - `to_payment_center_claims(self, claims: Iterable[Claim], pc_cache: PaymentCenterCache, pc_type: PaymentCenterType, ou_summary: OUSummary) -> list[PaymentCenterClaims]`
    - `attach_over_under(self, pc_claims: list[PaymentCenterClaims], ou_summary: OUSummary) -> None`

- Standalone:
  - `group_by_parent(claims: Iterable[Claim]) -> dict[str, ParentGroup]`

### `core/service_line_processor.py`
- Class: `ServiceLineProcessor`
  - Methods:
    - `compute_service_line(self, sl: ServiceLine, pe: PaymentEvent, context: PaymentContext) -> ServiceLinePayment`
    - `rollup_to_claim(self, group: ParentGroup) -> ClaimPayment`
    - `apply_interest(self, claim_payment: ClaimPayment, rules: InterestRules, due_date: date) -> ClaimPayment`


### `data/models/claim.py`
- Classes:
  - `Claim` (dataclass): ids, type, status, amounts, frequency, NPI, TIN, MemberID, ParentClaimCore_ID, OriginalClaimCore_ID, VoidClaimCore_ID, BenefitPlan_ID, service lines.
  - `ParentGroup` (dataclass): parent id, `paid`, `void`, `adjust`, service lines.
  - Enums/Constants: `ClaimType`, `ClaimStatus`, `FrequencyCode`.

### `data/models/payment.py`
- Classes:
  - `ServiceLine` (dataclass): codes, qty, amounts.
  - `ServiceLinePayment` (dataclass): computed components, offsets applied.
  - `ClaimPayment` (dataclass): aggregate of lines, interest.
  - `PaymentContext` (dataclass): PE config fragments, O/U info.

### `data/models/payment_center.py`
- Classes:
  - `PaymentCenter` (dataclass): id, vendor name, TaxID, NPI, member info, address.
  - `PaymentCenterType` (enum): `PROVIDER`, `DMR`.

### `data/models/over_under.py`
- Classes:
  - `OverUnderRecord` (dataclass): type, total, remaining, appliedThisCycle, references.
  - `OUSummary` (dataclass): per-PC aggregation, over and under totals/remaining.

### `data/models/event.py`
- Classes:
  - `PaymentEvent` (dataclass): id, business info, inclusion criteria id, funding source id, due date, type, stage.
  - `InclusionCriteria` (dataclass): allowed plans, allowed PCs.
  - `FundingSource` (dataclass): account/check number context.
  - `InterestRules` (dataclass): rates and business overrides.
  - `RunMode` (enum): `DRY_RUN`, `FINAL`.

### `data/models/stats.py`
- Classes:
  - `PaymentEventStats` (dataclass): totals, claim counts by type/status, error/warning counts, timings.
  - `Finding` (dataclass): severity, message, count, sample IDs.
  - `ValidationReport` (dataclass): list of findings, blocked flag.
  - `Totals` (dataclass): amounts by PC and overall.


### `data/repositories/claim_repository.py`
- Class: `ClaimRepository`
  - Methods:
    - `fetch_ws(self, payment_event_id: str, projection: Projection | None = None) -> Iterable[Claim]`
    - `fetch_fin(self, payment_event_id: str, projection: Projection | None = None) -> Iterable[Claim]`
    - `backup(self) -> BackupRef`

### `data/repositories/payment_repository.py`
- Class: `PaymentRepository`
  - Methods:
    - `persist_service_line(self, payment: ServiceLinePayment) -> None`
    - `persist_claim_aggregate(self, payment: ClaimPayment) -> None`
    - `calc_and_upsert_over_under(self, pe_id: str, pc_id: int, records: list[OverUnderRecord]) -> None`
    - `backup(self) -> BackupRef`

### `data/repositories/payment_center_repo.py`
- Class: `PaymentCenterRepository`
  - Methods:
    - `copy_to_ws(self, pc_ids: list[int]) -> None`
    - `create_ws(self, missing_keys: list[str]) -> CreatedWS`
    - `create_prod_if_missing(self, ws_created: CreatedWS) -> CreatedProd`
    - `get_cache(self, keys: list[str]) -> PaymentCenterCache`
    - `backup(self) -> BackupRef`

### `data/config/config_loader.py`
- Class: `ConfigLoader`
  - Methods:
    - `load_payment_event(self, payment_event_id: str) -> PaymentEvent`
    - `load_interest_config(self, pe: PaymentEvent) -> InterestRules`
    - `load_funding_source(self, pe: PaymentEvent) -> FundingSource`
    - `load_inclusion_criteria(self, pe: PaymentEvent) -> InclusionCriteria`
    - `validate(self, pe: PaymentEvent) -> None`


### `processing/parallel/multiprocessing.py`
- Functions:
  - `run_pc_level(tasks: Iterable[T], fn: Callable[[T], R], workers: int) -> list[R]`
  - `run_claim_batch_level(batches: Iterable[list[T]], fn: Callable[[list[T]], R], workers: int) -> list[R]`
  - `run_service_line_level(batches: Iterable[list[T]], fn: Callable[[list[T]], R], workers: int) -> list[R]`

### `processing/parallel/multithreading.py`
- Functions:
  - `thread_map(fn: Callable[[T], R], items: Iterable[T], workers: int) -> list[R]`
  - `thread_batch(fn: Callable[[list[T]], R], batches: Iterable[list[T]], workers: int) -> list[R]`

### `processing/optimization/batch_processor.py`
- Functions:
  - `batch_iterable(items: Iterable[T], size: int) -> Iterable[list[T]]`
  - `bulk_upsert(coll: Collection, docs: list[dict], ordered: bool = False) -> UpsertResult`
  - `allocate_sequence_chunks(name: str, chunk_size: int, workers: int) -> list[SequenceChunk]`


### `utils/logging.py`
- Functions:
  - `configure_logging(level: str = "INFO", json: bool = True) -> None`
  - `get_logger(name: str) -> logging.Logger`

### `utils/error_handling.py`
- Exception classes:
  - `PaymentProcessError`
  - `ValidationError`
  - `CriticalValidationError`
  - `RepositoryError`
  - `ConfigurationError`
  - `SequenceNumberError`
  - `ConcurrencyError`


## Standalone functions summary
- CLI: `build_arg_parser`, `parse_args`, `validate_args`, `main`.
- Parallelism: `run_pc_level`, `run_claim_batch_level`, `run_service_line_level`, `thread_map`, `thread_batch`.
- Batching: `batch_iterable`, `bulk_upsert`, `allocate_sequence_chunks`.
- Logging: `configure_logging`, `get_logger`.
- Processing helpers (optional): `group_by_parent`, `now_utc`, `stage_label`.


## Custom variables and configuration

### Environment variables (suggested)
- `PAYMENT_DB_URI` – connection string for datastore
- `PAYMENT_LOG_LEVEL` – default logging level (INFO/DEBUG)
- `PAYMENT_CONFIG_PATH` – external config path override
- `PAYMENT_MAX_WORKERS` – default workers (fallback: CPU count)
- `PAYMENT_BATCH_SIZE` – default batch size
- `PAYMENT_SEQ_CHUNK_SIZE` – allocation chunk size per worker

### Constants (in a shared `settings.py` or embedded per module)
- `DEFAULT_BATCH_SIZE = 1000`
- `DEFAULT_MAX_WORKERS = min(os.cpu_count() or 4, 8)`
- `SEQ_CHUNK_SIZE_DEFAULT = 5000`
- Severity labels: `SEV_CRITICAL`, `SEV_WARNING`, `SEV_INFO`

### Enums (models)
- `RunMode = {DRY_RUN, FINAL}`
- `PaymentCenterType = {PROVIDER, DMR}`
- `ClaimType`, `ClaimStatus`, `FrequencyCode`


## What goes in each __init__

- `PaymentProcess/__init__.py`
  - `from .core.payment_processor import PaymentProcessor`
  - `from .core.validation import Validation`
  - `from .core.payment_center import PaymentCenterManager`
  - `from .core.claim_processor import ClaimTransformer`
  - `from .core.service_line_processor import ServiceLineProcessor`
  - `__all__ = ["PaymentProcessor", "Validation", "PaymentCenterManager", "ClaimTransformer", "ServiceLineProcessor"]`
  - `__version__ = "0.1.0"`

- `PaymentProcess/core/__init__.py`
  - Re-export core classes for convenience.

- `PaymentProcess/data/__init__.py`, `PaymentProcess/data/models/__init__.py`, `PaymentProcess/data/repositories/__init__.py`
  - Re-export primary models and repositories (e.g., `PaymentEvent`, `PaymentCenter`, `ClaimRepository`, ...).

- `PaymentProcess/processing/__init__.py`, `PaymentProcess/processing/parallel/__init__.py`, `PaymentProcess/processing/optimization/__init__.py`
  - Re-export parallel/batch utilities.

- `PaymentProcess/utils/__init__.py`
  - Expose `configure_logging`, exceptions.


## CLI flow details

- `main.py`:
  1. Parse args via `argument.py`.
  2. Configure logging (`utils.logging.configure_logging`).
  3. Build repositories and config loader.
  4. Instantiate `PaymentProcessor`.
  5. Dispatch based on `--mode`:
     - `dry-run` -> `PaymentProcessor.run_dry_run(pe_id)`
     - `final` -> `PaymentProcessor.run_final_run(pe_id)`
  6. Print/serialize `PaymentEventStats`; exit code by severity.

- `argument.py` validation rules:
  - `--payment-event-id` must be non-empty.
  - `--mode` required and in {dry-run, final}.
  - `--workers`, `--batch-size` > 0.
  - If `--validate-only` then skip calculation steps.


## Tests (brief pointers)
- Unit tests per module (`tests/unit/...`):
  - Validation edge cases (invalid frequency, missing IDs, duplicates).
  - Claim transformation grouping and PC cache usage.
  - Service line computation roundings and interest.
  - Batch utilities: chunking, sequence allocation.
- Integration tests (`tests/integration/...`):
  - Dry Run on synthetic dataset -> PaymentEventStats correctness.
  - Final Run full path -> O/U persistence and aggregates.


## Notes and next steps
- This structure is implementation-ready. Start by scaffolding packages, dataclasses, and the CLI.
- Add a central `settings.py` if preferred to consolidate constants and env parsing.
- Ensure repository implementations align with actual datastore (MongoDB/SQL/etc.).
- Consider `pydantic` or `dataclasses` for models and validation.
