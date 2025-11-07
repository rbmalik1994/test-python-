"""Payment event configuration models powered by Pydantic."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Set

from pydantic import BaseModel, ConfigDict, Field


class RunMode(str, Enum):
    """Execution modes supported by the PaymentProcessor."""

    DRY_RUN = "dry-run"
    FINAL = "final"


class InclusionCriteria(BaseModel):
    """Criteria used to include claims in the PaymentEvent."""

    allowed_benefit_plans: Set[str] = Field(default_factory=set)
    allowed_payment_centers: Set[int] = Field(default_factory=set)

    model_config = ConfigDict(extra="forbid")


class FundingSource(BaseModel):
    """Funding source associated with a PaymentEvent."""

    account_number: str
    description: str

    model_config = ConfigDict(extra="forbid")


class InterestRules(BaseModel):
    """Rules controlling interest calculations."""

    rate: float
    grace_period_days: int

    model_config = ConfigDict(extra="forbid")


class PaymentEvent(BaseModel):
    """Root configuration entity describing a payment event."""

    payment_event_id: str
    business_id: str
    inclusion_criteria_id: str
    funding_source_id: str
    due_date: date
    event_type: str
    stage: str
    run_mode: RunMode
    allowed_plans: List[str] = Field(default_factory=list)
    allowed_payment_center_types: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")
