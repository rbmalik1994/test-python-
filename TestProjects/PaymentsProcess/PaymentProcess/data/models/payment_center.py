"""PaymentCenter data models built on Pydantic."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field


class PaymentCenterType(str, Enum):
    """Types of payment centers supported by the system."""

    PROVIDER = "PROVIDER"
    DMR = "DMR"


class PaymentCenter(BaseModel):
    """Representation of a PaymentCenter entity."""

    payment_center_id: int
    name: str
    tax_id: str | None = None
    npi: str | None = None
    member_id: str | None = None
    address: str | None = None

    model_config = ConfigDict(extra="allow")


PaymentCenterCache = Dict[str, int]
"""In-memory mapping from composite keys to PaymentCenter IDs."""


class PaymentCenterSummary(BaseModel):
    """Aggregate information produced during PaymentCenter synchronization."""

    existing_ids: List[int] = Field(default_factory=list)
    created_ws_ids: List[int] = Field(default_factory=list)
    created_prod_ids: List[int] = Field(default_factory=list)
    missing_keys: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class PaymentCenterClaims(BaseModel):
    """Container for claim data grouped by PaymentCenter."""

    payment_center_id: int
    claim_ids: List[str] = Field(default_factory=list)
    totals: dict[str, float] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")
