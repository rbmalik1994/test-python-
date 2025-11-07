"""Top-level package for the PaymentProcess application skeleton.

This module exposes the primary entry points for downstream consumers while
keeping implementation details organized within subpackages. The project is
structured for extensibility and testability, enabling teams to implement the
full payment event lifecycle in iterative steps.
"""

from .core.payment_processor import PaymentProcessor
from .core.validation import Validation
from .core.payment_center import PaymentCenterManager
from .core.claim_processor import ClaimTransformer
from .core.service_line_processor import ServiceLineProcessor

__all__ = [
    "PaymentProcessor",
    "Validation",
    "PaymentCenterManager",
    "ClaimTransformer",
    "ServiceLineProcessor",
]

__version__ = "0.1.0"
