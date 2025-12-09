"""Claim model definitions used across PaymentProcess.

All domain entities leverage :class:`pydantic.BaseModel` so large batches of
MongoDB documents can be validated in one pass via ``model_validate`` calls.
"""

from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class ClaimType(str, Enum):
    """Enumerate supported claim types (e.g., medical, pharmacy)."""

    MEDICAL = "MEDICAL"
    PHARMACY = "PHARMACY"
    DENTAL = "DENTAL"


class ClaimStatus(str, Enum):
    """Enumerate claim processing statuses."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    ADJUSTED = "ADJUSTED"


class FrequencyCode(str, Enum):
    """Enumerate allowed billing frequency codes."""

    ORIGINAL = "1"
    INTERIM_CONTINUING = "2"
    INTERIM_FINAL = "3"
    REPLACEMENT = "4"
    VOID = "5"


class ServiceLineCore(BaseModel):
    """Lightweight representation of a claim service line for skeleton purposes."""

    service_code: str
    billed_amount: float
    allowed_amount: float

    model_config = ConfigDict(extra="forbid")


class Claim(BaseModel):
    """Domain model representing a claim sourced from Mongo collections.

    Use :meth:`Claim.model_validate` to coerce raw Mongo documents into strongly
    typed models before downstream processing.
    """

    claim_id: str
    parent_claim_core_id: str
    claim_type: ClaimType
    status: ClaimStatus
    frequency_code: FrequencyCode
    tin: str | None = None
    npi: str | None = None
    member_id: str | None = None
    benefit_plan_id: str | None = None
    service_lines: List[ServiceLineCore] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class ParentGroup(BaseModel):
    """Grouping of claims by parent identifier for aggregation."""

    parent_id: str
    paid_claims: List[Claim] = Field(default_factory=list)
    void_claims: List[Claim] = Field(default_factory=list)
    adjust_claims: List[Claim] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    def add_claim(self, claim: Claim) -> None:
        """Assign a claim to the appropriate category inside the group."""

        if claim.frequency_code == FrequencyCode.VOID:
            self.void_claims.append(claim)
        elif claim.status == ClaimStatus.ADJUSTED or claim.frequency_code in {
            FrequencyCode.REPLACEMENT,
            FrequencyCode.INTERIM_FINAL,
        }:
            self.adjust_claims.append(claim)
        else:
            self.paid_claims.append(claim)
