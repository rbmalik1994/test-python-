"""CLI argument parsing and validation for PaymentProcess.

Exposes:
- build_arg_parser()
- parse_args()
- validate_args()
"""
from __future__ import annotations

import argparse
import os


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="payment-process",
        description="Run PaymentEvent processing (dry-run/final)"
    )
    parser.add_argument("--payment-event-id", "-p", required=True, help="PaymentEvent identifier")
    parser.add_argument(
        "--mode", "-m", required=True, choices=["dry-run", "final"], help="Run mode"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=int(os.getenv("PAYMENT_MAX_WORKERS", "0") or 0),
        help="Number of worker processes/threads (default from env or CPU heuristic)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=int(os.getenv("PAYMENT_BATCH_SIZE", "1000") or 1000),
        help="Batch size for processing (default 1000)",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("PAYMENT_LOG_LEVEL", "INFO"),
        help="Logging level (default INFO)",
    )
    parser.add_argument(
        "--config-path",
        default=os.getenv("PAYMENT_CONFIG_PATH"),
        help="Path to external configuration file (optional)",
    )
    parser.add_argument(
        "--db-uri",
        default=os.getenv("PAYMENT_DB_URI"),
        help="Override datastore connection string (optional; else use env PAYMENT_DB_URI)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume a failed run where safe",
    )
    parser.add_argument(
        "--pc-type",
        choices=["provider", "dmr"],
        help="Override PaymentCenter type (optional)",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Run validations only without calculations",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = build_arg_parser()
    ns = parser.parse_args(argv)
    validate_args(ns)
    return ns


def validate_args(ns: argparse.Namespace) -> None:
    if not ns.payment_event_id:
        raise SystemExit("--payment-event-id is required and must be non-empty")
    if ns.mode not in ("dry-run", "final"):
        raise SystemExit("--mode must be one of: dry-run, final")
    if ns.workers is not None and ns.workers < 0:
        raise SystemExit("--workers must be >= 0")
    if ns.batch_size is not None and ns.batch_size <= 0:
        raise SystemExit("--batch-size must be > 0")
    # DB URI can be None here; main will resolve from env/args and validate then
