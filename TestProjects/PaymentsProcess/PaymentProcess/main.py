"""CLI entry point for the PaymentProcess application skeleton.

This module wires together argument parsing, logging configuration, and the
high-level orchestration object. The goal is to keep business logic outside of
this file so the CLI remains a thin wrapper that is easy to test and extend.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from . import PaymentProcessor
from .argument import parse_args, validate_args
from .utils.load_env import get_env_config
from .utils.mongo_db import close_mongo_client, get_mongo_client
from .utils.logging import configure_logging


REQUIRED_ENV_VARS: tuple[str, ...] = ("PAYMENT_DB_URI",)
"""Environment variables that satisfy defaults for CLI options."""


def main(argv: Iterable[str] | None = None) -> int:
    """Run the PaymentProcess CLI workflow.

    Parameters
    ----------
    argv:
        Optional iterable of command-line arguments. When ``None`` the current
        process arguments are used, mirroring :func:`argparse.ArgumentParser.parse_args`.

    Returns
    -------
    int
        Exit code: ``0`` for success, non-zero for critical errors. Callers
        should convert raised exceptions into appropriate exit codes.
    """

    args = parse_args(list(argv) if argv is not None else None)

    env_override = Path(args.env_file).expanduser() if args.env_file else None
    env_config = get_env_config(env_name=args.env_name, env_path=env_override)

    validate_args(args, REQUIRED_ENV_VARS)

    configure_logging(level=args.log_level or "INFO")

    db_uri = args.db_uri or env_config.payment_db_uri
    args.db_uri = db_uri

    connection = get_mongo_client(db_uri)

    processor = PaymentProcessor.from_connection(
        connection=connection,
        cli_args=args,
    )

    payment_event_id = args.payment_event_id

    try:
        if args.mode == "dry-run":
            processor.run_dry_run(payment_event_id)
        else:
            processor.run_final_run(payment_event_id)
    finally:
        close_mongo_client()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
