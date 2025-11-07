# Coding Guidelines

The skeleton intentionally favors explicit docstrings and type hints to make it
clear where production logic should live. Adopt the following conventions while
filling in the implementation.

## Architecture and modular boundaries
- Keep orchestration and business workflows inside `core/`.
- Use repositories exclusively for datastore access; avoid business logic in repositories.
- Reserve `processing/` for parallelism, batching, and long‑running job primitives. Pool lifecycle is owned by helpers in `processing/parallel/`.
- Keep modules small and cohesive; design public, stable interfaces and hide implementation details behind them.

## Data models
- Use `pydantic.BaseModel` for domain entities.
- Configure models with `extra="forbid"`, `validate_assignment=True`, and prefer `frozen=True` for immutability where feasible.
- Convert Mongo documents in bulk with `model_validate` and serialize with `model_dump(mode="json", by_alias=True, exclude_none=True)` when writing back.
- Prefer `UUID`, `Decimal`, `datetime` (timezone‑aware, UTC) and `Enum` for stronger domain types.
- Use `field_validator`/`model_validator` for invariants; keep cross‑entity invariants in services.

## Docstrings
- Use NumPy‑style docstrings for all public modules, classes, and functions.
- Include Parameters, Returns, Raises, Examples, and Notes sections where helpful.
- Document side effects, timeouts, thread/process requirements, and idempotency.

## Type hints
- Annotate all public APIs; avoid `Any` in public signatures.
- Use forward references (`"TypeName"`) and `Protocol`/`TypedDict` for contracts where concrete types aren’t known.
- Prefer `Iterable`/`Mapping` over concrete containers in parameters; return concrete types.
- Use `Literal`/`Final`/`NewType` where it improves correctness.

## Exceptions
- Raise the most specific exception from `utils.error_handling`.
- Convert low‑level errors (I/O, driver, parsing) into high‑level categories before propagating.
- Preserve context via exception chaining (`raise X from err`) but avoid leaking sensitive data in messages.

## Logging and observability
- Use `utils.logging.get_logger(__name__)` to obtain module loggers.
- Log structured events with stable keys (e.g., `event`, `entity_id`, `elapsed_ms`).
- Never log secrets, tokens, or PII; prefer redaction helpers.
- Include correlation/request IDs and execution context where available.

## Configuration and secrets
- Follow 12‑factor: read config from environment or a dedicated settings object.
- Provide safe defaults for development; require explicit values in production.
- Load secrets from environment or secret stores; never commit secrets to VCS.

## Repositories and data access
- Keep repository methods simple, composable, and side‑effect‑free beyond I/O.
- Apply timeouts, pagination, and limits; avoid N+1 patterns.
- Create indexes for query patterns; validate query plans in integration tests.
- Prefer bulk operations, idempotent upserts, and transactions where supported.

## Concurrency and parallelism
- Never share mutable state across processes/threads without explicit synchronization.
- Use helpers in `processing/parallel/` for pool lifecycle, backpressure, and graceful shutdown.
- Be explicit about timeouts, retries, and cancellation. Propagate cancellation promptly.
- Make jobs idempotent; persist progress to allow safe retries.

## Testing
- Unit tests live in `tests/unit/`; integration tests in `tests/integration/`.
- Use dependency injection so collaborators can be faked or stubbed.
- Name tests `test_*.py` and one assertion intent per test; prefer parameterization.
- Aim for ≥90% line coverage on `core/` and `utils/`; measure branch coverage for critical paths.
- Use fixtures for common setup and factories/builders for test data.
- Mark slow/external tests and isolate with containers or ephemeral resources.

## Style, linting, and static analysis
- Use a single formatter (e.g., Black) and an import organizer (e.g., isort). Do not hand‑format.
- Enforce linting (e.g., Ruff/Flake8) and type checking (e.g., MyPy) in CI; treat warnings as errors.
- Keep functions short; extract helpers when cyclomatic complexity grows.

## API and serialization
- Keep public functions pure when possible; avoid hidden I/O and global state.
- Use Pydantic encoders for `datetime`, `Decimal`, and `UUID`. Do not rely on `str(datetime)`.
- Define stable JSON schemas; version breaking changes and support migrations.

## Performance and reliability
- Prefer streaming/generators over loading large datasets into memory.
- Measure before optimizing; use profiling and tracing to find hotspots.
- Add exponential backoff with jitter for transient errors; cap retries.

## Time, money, and locale
- Use timezone‑aware UTC datetimes end‑to‑end.
- Represent currency with `Decimal` and explicit currency codes; never float for money.
- Normalize and validate external locale/data at the boundary.

## Git, reviews, and releases
- Use small, focused PRs with clear titles and checklists.
- Follow Conventional Commits (feat, fix, chore, docs, refactor, test, perf) and branch naming (`feature/…`, `fix/…`).
- Keep CHANGELOG up to date; use semantic versioning for published artifacts.

## Documentation
- Update README and module docs alongside code changes.
- Record significant decisions as ADRs under `docs/adr/`.

## Ready‑to‑merge checklist
- [ ] Public APIs typed and documented; no `Any` leaks.
- [ ] Errors mapped to `utils.error_handling`; messages redact sensitive data.
- [ ] Logs are structured; no secrets in logs; correlation IDs included where applicable.
- [ ] Concurrency considerations documented; cancellation and timeouts enforced.
- [ ] Tests added/updated; coverage acceptable; flaky tests eliminated.
- [ ] Lint, format, and type checks pass locally and in CI.
- [ ] Backwards compatibility and migrations addressed (data, APIs, configs).
- [ ] Documentation updated (README, ADRs, examples).
