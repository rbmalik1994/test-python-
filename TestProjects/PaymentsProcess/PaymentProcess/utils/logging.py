"""Logging utilities for PaymentProcess."""

from __future__ import annotations

import logging


def configure_logging(level: str = "INFO", json: bool = True) -> None:
    """Configure application-wide logging.

    Parameters
    ----------
    level:
        Logging level name (e.g., ``INFO`` or ``DEBUG``).
    json:
        Toggle for JSON-structured logging. The placeholder implementation
        sticks to the standard logging formatter until a structured logger is
        integrated.
    """

    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO))

    if json:
        # Placeholder hook for JSON logging integration.
        logging.getLogger(__name__).debug("JSON logging not yet implemented.")


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger."""

    return logging.getLogger(name)
