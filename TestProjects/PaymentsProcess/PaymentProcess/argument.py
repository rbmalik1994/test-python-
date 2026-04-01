"""Command-line interface helpers for the PaymentProcess project.

The functions in this module centralize argument parsing and validation rules
so they can be reused by both the CLI entry point and test harnesses. Keep
business-specific rules in the core layer; limit this module to surface-level
validation and configuration wiring.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable, Sequence


PAYMENT_CENTER_MODES: tuple[str, ...] = ("pc-validation", "pc-create")
PAYMENT_EVENT_MODES: tuple[str, ...] = ("dry-run", "final", "rollback")
SUPPORTED_RUN_MODES: tuple[str, ...] = PAYMENT_CENTER_MODES + PAYMENT_EVENT_MODES


def build_arg_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser used by the CLI.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured with all supported CLI flags. Update this function
        when introducing new CLI options so that documentation and validation
        logic stay centralized.
    """

    parser = argparse.ArgumentParser(
        prog="payment-process",
        description=(
            "Execute categorized payment runs: Payment Center "
            "(Validation/Create) and Payment Event (Dry Run/Final/Rollback)."
        ),
    )

    parser.add_argument(
        "--payment-event-id",
        "-p",
        required=True,
        help="Identifier of the PaymentEvent to process.",
    )
    parser.add_argument(
        "--mode",
        "-m",
        choices=SUPPORTED_RUN_MODES,
        required=True,
        help=(
            "Run category mode: pc-validation | pc-create | dry-run | final | "
            "rollback."
        ),
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Override the worker pool size. Defaults to env or CPU heuristic.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Override batch sizing for claim/service-line processing.",
    )
    parser.add_argument(
        "--log-level",
        default=None,
        help="Set logging level (INFO, DEBUG, etc.). Defaults to env setting.",
    )
    parser.add_argument(
        "--db-uri",
        default=None,
        help="Datastore connection string. Falls back to PAYMENT_DB_URI env.",
    )

    parser.add_argument(
        "--env-file",
        default=None,
        help="Optional path to a .env file that overrides the default env config.",
    )
    parser.add_argument(
        "--env-name",
        "-e",
        default=None,
        help=(
            "Logical environment name (qa1, dev, prod, etc.). "
            "Automatically loads data/config/.env.<env>."
        ),
    )

    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse arguments and perform lightweight validation.

    Parameters
    ----------
    argv:
        Optional sequence of CLI arguments. The default of ``None`` instructs
        :mod:`argparse` to read the current process arguments, enabling both
        programmatic invocation and CLI usage.

    Returns
    -------
    argparse.Namespace
        Parsed arguments ready for downstream consumption. The returned
        namespace should be passed to :func:`validate_args` for semantic checks.
    """

    parser = build_arg_parser()
    return parser.parse_args(argv)


def validate_args(ns: argparse.Namespace, required_env: Iterable[str] | None = None) -> None:
    """Validate parsed arguments and ensure required invariants hold.

    Parameters
    ----------
    ns:
        Parsed arguments produced by :func:`parse_args`.
    required_env:
        Optional iterable of environment variable names that must be provided
        when certain CLI overrides (such as ``--db-uri``) are omitted. Keeping
        the value external makes unit testing easier.

    Raises
    ------
    ValueError
        If validation fails. The caller should handle this exception and
        convert it to a user-facing error, exiting with a non-zero status code.
    """

    if ns.workers is not None and ns.workers <= 0:
        raise ValueError("--workers must be a positive integer when provided.")

    if ns.batch_size is not None and ns.batch_size <= 0:
        raise ValueError("--batch-size must be a positive integer when provided.")

    if ns.mode not in set(SUPPORTED_RUN_MODES):
        raise ValueError(
            "--mode must be one of: " + ", ".join(SUPPORTED_RUN_MODES)
        )

    if ns.env_file:
        env_path = Path(ns.env_file).expanduser()
        if not env_path.is_file():
            raise ValueError(f"--env-file does not point to a readable file: {env_path}")

    if ns.env_name and any(sep in ns.env_name for sep in ("/", "\\")):
        raise ValueError("--env-name should be a simple token without path separators.")

    if getattr(ns, "db_uri", None):
        return

    missing_env: list[str] = []
    if required_env:
        for env_var in required_env:
            if not os.environ.get(env_var):
                missing_env.append(env_var)

    if missing_env:
        raise ValueError(
            "--db-uri is required when environment variables are unavailable: "
            + ", ".join(sorted(set(missing_env)))
        )
