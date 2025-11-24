"""Executable guide for the PaymentProcess error hierarchy.

Run this module directly to see how every custom exception from
``error_handling.py`` can be raised, annotated with context, and handled.
"""

from __future__ import annotations

from pprint import pprint

from error_handling import (
    ClaimNotFoundError,
    ConfigurationError,
    ConcurrencyError,
    CriticalValidationError,
    DataIntegrityError,
    DuplicatePaymentError,
    EntityNotFoundError,
    ExternalServiceError,
    MissingConfigurationError,
    PaymentNotFoundError,
    PaymentProcessError,
    ProcessingStateError,
    RepositoryConnectionError,
    RepositoryError,
    RetryableError,
    SequenceNumberError,
    ServiceResponseError,
    ServiceTimeoutError,
    TransientRepositoryError,
    ValidationError,
)


def _show(error: PaymentProcessError) -> None:
    """Print the error, its retry hint (if any), and its contextual payload."""

    print(f"\n[{error.__class__.__name__}] {error}")
    retry_after = getattr(error, "retry_after", None)
    if retry_after is not None:
        print(f"  retry_after: {retry_after:.2f}s")
    if error.context:
        print("  context:")
        pprint(error.context, indent=4)


def demonstrate_base_error() -> None:
    """Show the base class carrying arbitrary diagnostic context."""

    _show(
        PaymentProcessError(
            "Unhandled orchestration failure",
            context={"stage": "bootstrap", "workflow_id": "wf-001"},
        )
    )


def demonstrate_validation_errors() -> None:
    """Highlight the non-critical and critical validation layers."""

    _show(
        ValidationError(
            "Policy number format is deprecated",
            context={"field": "policy_number", "value": "ABC-123"},
        )
    )
    _show(
        CriticalValidationError(
            "Primary insured date of birth missing",
            context={"claim_id": "CLM-9001"},
        )
    )
    _show(
        DuplicatePaymentError(
            "Duplicate payment detected",
            context={"payment_id": "PMT-123", "existing_reference": "chk-009"},
        )
    )
    _show(
        DataIntegrityError(
            "Service lines do not balance",
            context={"expected_total": 1500.00, "actual_total": 1475.25},
        )
    )


def demonstrate_repository_errors() -> None:
    """Cover repository failures, including retryable variants."""

    _show(
        RepositoryError(
            "Failed to persist payment",
            context={"payment_id": "PMT-404", "operation": "insert"},
        )
    )
    _show(
        RepositoryConnectionError(
            "MongoDB cluster unreachable",
            context={"cluster": "primary", "host": "mongo.internal"},
        )
    )
    _show(
        EntityNotFoundError(
            "Requested entity missing",
            context={"entity": "PaymentCenter", "identifier": "NOVA"},
        )
    )
    _show(
        ClaimNotFoundError(
            "Claim not found",
            context={"claim_id": "CLM-0007"},
        )
    )
    _show(
        PaymentNotFoundError(
            "Payment record missing",
            context={"payment_id": "PMT-777"},
        )
    )
    _show(
        TransientRepositoryError(
            "Write concern timeout",
            retry_after=2.5,
            context={"collection": "payments", "attempt": 1},
        )
    )


def demonstrate_configuration_errors() -> None:
    """Emphasize configuration validation during startup."""

    _show(
        ConfigurationError(
            "Currency conversion table missing",
            context={"module": "fx_adapter"},
        )
    )
    _show(
        MissingConfigurationError(
            "payment_center.partition_key not configured",
            context={"env": "prod"},
        )
    )


def demonstrate_state_management_errors() -> None:
    """Surface issues that arise from workflow coordination."""

    _show(
        SequenceNumberError(
            "Unable to allocate claim sequence",
            context={"claim_id": "CLM-22"},
        )
    )
    _show(
        ProcessingStateError(
            "Cannot move claim from APPROVED to VALIDATING",
            context={"claim_id": "CLM-22", "from": "APPROVED", "to": "VALIDATING"},
        )
    )
    _show(
        ConcurrencyError(
            "Lock acquisition timed out",
            context={"resource": "claim:CLM-22", "wait_seconds": 5},
        )
    )


def demonstrate_external_service_errors() -> None:
    """Demonstrate failures when calling upstream or downstream services."""

    _show(
        ExternalServiceError(
            "Eligibility service responded with HTTP 500",
            context={"service": "eligibility", "request_id": "req-101"},
        )
    )
    _show(
        ServiceTimeoutError(
            "EDI submission timed out",
            retry_after=10.0,
            context={"gateway": "clearinghouse", "attempt": 2},
        )
    )
    _show(
        ServiceResponseError(
            "Received malformed JSON payload",
            context={"service": "remit_api", "response_snippet": "<html>"},
        )
    )


def demonstrate_retryable_error() -> None:
    """Show how retry hints can be communicated in a generic way."""

    _show(
        RetryableError(
            "Background sync is throttled",
            retry_after=1.25,
            context={"operation": "sync_payments", "next_window": "+1s"},
        )
    )


def run_all_examples() -> None:
    """Execute the complete demonstration suite."""

    scenarios = [
        demonstrate_base_error,
        demonstrate_validation_errors,
        demonstrate_repository_errors,
        demonstrate_configuration_errors,
        demonstrate_state_management_errors,
        demonstrate_external_service_errors,
        demonstrate_retryable_error,
    ]

    for scenario in scenarios:
        print(f"\n=== {scenario.__name__} ===")
        scenario()


if __name__ == "__main__":
    run_all_examples()
