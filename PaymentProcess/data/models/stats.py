"""Statistics and validation result models backed by Pydantic."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field


class Finding(BaseModel):
    """Represents a single validation finding."""

    severity: str
    message: str
    count: int = 0
    sample_ids: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class ValidationReport(BaseModel):
    """Aggregate validation findings and overall status."""

    findings: List[Finding] = Field(default_factory=list)
    blocked: bool = False

    model_config = ConfigDict(extra="forbid")


class Totals(BaseModel):
    """Aggregate monetary totals for a PaymentEvent."""

    by_payment_center: Dict[int, float] = Field(default_factory=dict)
    overall: float = 0.0

    model_config = ConfigDict(extra="forbid")


class SequenceReport(BaseModel):
    """Summaries of sequence usage and expected values."""

    expected: Dict[str, int] = Field(default_factory=dict)
    actual: Dict[str, int] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


class PaymentEventStats(BaseModel):
    """Statistics collected during a PaymentEvent run."""

    payment_event_id: str
    stage: str
    total_claims: int
    totals: Totals = Field(default_factory=Totals)
    started_at: datetime
    completed_at: datetime | None = None
    findings: ValidationReport = Field(default_factory=ValidationReport)

    model_config = ConfigDict(extra="forbid")
