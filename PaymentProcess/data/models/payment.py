"""Payment calculation models built on Pydantic."""

from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field

from .over_under import OUSummary


class ServiceLine(BaseModel):
    """Representation of a service line ready for calculation."""

    service_code: str
    charge_amount: float
    allowed_amount: float
    quantity: float

    model_config = ConfigDict(extra="forbid")


class ServiceLinePayment(BaseModel):
    """Calculated payment details for a single service line."""

    service_line: ServiceLine
    calculated_amount: float
    offsets_applied: float
    metadata: Dict[str, float] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


class ClaimPayment(BaseModel):
    """Aggregate payment information at the claim level."""

    claim_id: str
    service_line_payments: List[ServiceLinePayment] = Field(default_factory=list)
    total_amount: float
    interest_amount: float = 0.0

    model_config = ConfigDict(extra="allow")


class PaymentContext(BaseModel):
    """Contextual data required for payment calculations."""

    payment_event_id: str
    over_under: OUSummary
    settings: dict[str, float] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")
