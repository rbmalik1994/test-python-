"""Custom exception hierarchy for PaymentProcess."""

from __future__ import annotations

from typing import Any, Mapping

__all__ = [
    "PaymentProcessError",
    "ValidationError",
    "CriticalValidationError",
    "DuplicatePaymentError",
    "DataIntegrityError",
    "RepositoryError",
    "RepositoryConnectionError",
    "EntityNotFoundError",
    "ClaimNotFoundError",
    "PaymentNotFoundError",
    "TransientRepositoryError",
    "ConfigurationError",
    "MissingConfigurationError",
    "SequenceNumberError",
    "ProcessingStateError",
    "ConcurrencyError",
    "ExternalServiceError",
    "ServiceTimeoutError",
    "ServiceResponseError",
    "RetryableError",
]


class PaymentProcessError(Exception):
    """Base exception for PaymentProcess-specific errors."""

    def __init__(
        self,
        message: str | None = None,
        *,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        self.context: dict[str, Any] = dict(context) if context else {}
        super().__init__(message or self.__class__.__name__)

    def with_context(self, **context: Any) -> PaymentProcessError:
        """Return the same exception enriched with extra context."""

        self.context.update(context)
        return self


class ValidationError(PaymentProcessError):
    """Raised for non-critical validation issues."""


class CriticalValidationError(ValidationError):
    """Raised when validation issues should block processing."""


class DuplicatePaymentError(CriticalValidationError):
    """Raised when a payment record collides with an existing one."""


class DataIntegrityError(ValidationError):
    """Raised when inbound data fails structural or semantic checks."""


class RepositoryError(PaymentProcessError):
    """Raised when repository operations fail."""


class RepositoryConnectionError(RepositoryError):
    """Raised when persistence backends are unreachable."""


class EntityNotFoundError(RepositoryError):
    """Raised when a requested entity is missing from the repository."""


class ClaimNotFoundError(EntityNotFoundError):
    """Raised when a claim lookup fails."""


class PaymentNotFoundError(EntityNotFoundError):
    """Raised when a payment lookup fails."""


class RetryableError(PaymentProcessError):
    """Indicates the operation may succeed on a subsequent attempt."""

    def __init__(
        self,
        message: str | None = None,
        *,
        retry_after: float | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message, context=context)


class TransientRepositoryError(RetryableError, RepositoryError):
    """Raised for temporary repository failures that should be retried."""


class ConfigurationError(PaymentProcessError):
    """Raised for configuration-related failures."""


class MissingConfigurationError(ConfigurationError):
    """Raised when a required configuration segment is absent."""


class SequenceNumberError(PaymentProcessError):
    """Raised when sequence number allocation fails."""


class ProcessingStateError(PaymentProcessError):
    """Raised when processing state transitions become invalid."""


class ConcurrencyError(PaymentProcessError):
    """Raised when concurrency primitives fail or deadlock."""


class ExternalServiceError(PaymentProcessError):
    """Raised when communicating with upstream or downstream services fails."""


class ServiceTimeoutError(RetryableError, ExternalServiceError):
    """Raised when a service call times out but may succeed later."""


class ServiceResponseError(ExternalServiceError):
    """Raised when a service responds with invalid or unexpected data."""
