"""Custom exception hierarchy for PaymentProcess."""

from __future__ import annotations


class PaymentProcessError(Exception):
    """Base exception for PaymentProcess-specific errors."""


class ValidationError(PaymentProcessError):
    """Raised for non-critical validation issues."""


class CriticalValidationError(ValidationError):
    """Raised when validation issues should block processing."""


class RepositoryError(PaymentProcessError):
    """Raised when repository operations fail."""


class ConfigurationError(PaymentProcessError):
    """Raised for configuration-related failures."""


class SequenceNumberError(PaymentProcessError):
    """Raised when sequence number allocation fails."""


class ConcurrencyError(PaymentProcessError):
    """Raised when concurrency primitives fail or deadlock."""
