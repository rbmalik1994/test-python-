"""Over/Under payment lifecycle models backed by Pydantic."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class OverUnderRecord(BaseModel):
    """Represents a single over/under payment entry."""

    reference: str
    amount: float
    type: str

    model_config = ConfigDict(extra="forbid")


class OUSummary(BaseModel):
    """Aggregated over/under info for a PaymentCenter."""

    payment_center_id: int
    previous_balance: float
    records: List[OverUnderRecord] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")
