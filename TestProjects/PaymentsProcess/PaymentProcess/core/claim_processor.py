"""Claim retrieval and transformation helpers."""

from __future__ import annotations

from typing import Iterable, List, Literal

from ..data.models.claim import Claim, ClaimStatus, ClaimType, FrequencyCode, ParentGroup
from ..data.models.event import PaymentEvent
from ..data.models.over_under import OUSummary
from ..data.models.payment_center import PaymentCenterCache, PaymentCenterClaims, PaymentCenterType
from ..data.repositories.claim_repository import ClaimRepository

ClaimSource = Literal["ws", "fin"]
"""Shorthand type for identifying claim source collections."""


class ClaimTransformer:
    """Transform claims into PaymentCenter-focused structures.

    The transformer should encapsulate:

    - Retrieval from either working-set or production claim collections.
    - Normalizing raw claim documents into :class:`PaymentCenterClaims`.
    - Annotating the transformed claims with over/under context so the payment
      processor can make allocation decisions without further lookups.
    """

    def __init__(self, repository: ClaimRepository | None = None) -> None:
        self._last_source: str | None = None
        self._repository = repository

    def fetch_claims(self, source: ClaimSource, payment_event: PaymentEvent) -> Iterable[Claim]:
        """Fetch claims from the configured repository.

        Implementations typically delegate to :class:`ClaimRepository`. Keep
        this method thin so tests can stub it easily. Repository helpers should
        bulk load MongoDB documents and use :meth:`Claim.model_validate` to
        return hydrated Pydantic models.
        """

        self._last_source = source
        if self._repository:
            fetcher = self._repository.fetch_ws if source == "ws" else self._repository.fetch_fin
            return list(fetcher(payment_event.payment_event_id, getattr(payment_event, "db_uri", "")))

        claims: list[Claim] = []
        plans = payment_event.allowed_plans or ["PLAN-A"]
        for idx, plan in enumerate(plans, start=1):
            claims.append(
                Claim(
                    claim_id=f"{payment_event.payment_event_id}-{source}-{idx}",
                    parent_claim_core_id=f"PARENT-{idx}",
                    claim_type=ClaimType.MEDICAL,
                    status=ClaimStatus.CLOSED if idx % 2 else ClaimStatus.OPEN,
                    frequency_code=FrequencyCode.ORIGINAL,
                    tin=f"TIN-{idx}",
                    npi=f"NPI-{idx}",
                    member_id=f"MEM-{idx}",
                    benefit_plan_id=plan,
                    service_lines=[],
                )
            )
        return claims

    def to_payment_center_claims(
        self,
        claims: Iterable[Claim],
        pc_cache: PaymentCenterCache,
        pc_type: PaymentCenterType,
        ou_summary: OUSummary,
    ) -> List[PaymentCenterClaims]:
        """Convert raw claims into PaymentCenterClaims shape.

        Expect to perform grouping by PaymentCenter key, parent aggregation,
        and initial statistics (counts, totals) to aid downstream processors.
        """

        grouped = group_by_parent(claims)
        pc_claims: list[PaymentCenterClaims] = []
        for parent_id, group in grouped.items():
            claim_ids = [claim.claim_id for claim in group.paid_claims + group.adjust_claims + group.void_claims]
            if not claim_ids:
                continue
            sample_claim = group.paid_claims[0] if group.paid_claims else group.adjust_claims[0]
            key = self._derive_pc_key(sample_claim, pc_type)
            payment_center_id = pc_cache.get(key)
            if payment_center_id is None:
                payment_center_id = len(pc_cache) + 1
                pc_cache[key] = payment_center_id
            totals = {
                "claims": len(claim_ids),
                "service_lines": sum(len(claim.service_lines) for claim in group.paid_claims),
                "projected_payment": sum(
                    sum(sl.allowed_amount for sl in claim.service_lines)
                    for claim in group.paid_claims
                ),
            }
            pc_claims.append(
                PaymentCenterClaims(
                    payment_center_id=payment_center_id,
                    claim_ids=claim_ids,
                    totals=totals,
                )
            )

        self.attach_over_under(pc_claims, ou_summary)
        return pc_claims

    def attach_over_under(
        self,
        pc_claims: List[PaymentCenterClaims],
        ou_summary: OUSummary,
    ) -> None:
        """Attach over/under payment context to PaymentCenter claims.

        This hook should merge existing O/U balances so final calculations can
        apply offsets. Keep the mutation localized to avoid widespread side
        effects.
        """

        if not ou_summary:
            return
        for entry in pc_claims:
            if entry.payment_center_id != ou_summary.payment_center_id:
                continue
            entry.totals["previous_balance"] = ou_summary.previous_balance
            entry.totals["ou_records"] = len(ou_summary.records)

    def _derive_pc_key(self, claim: Claim, pc_type: PaymentCenterType) -> str:
        if pc_type == PaymentCenterType.PROVIDER:
            identifier = claim.tin or claim.npi or claim.member_id or "UNKNOWN"
        else:
            identifier = claim.member_id or claim.benefit_plan_id or "UNKNOWN"
        return f"{pc_type.value}:{identifier}"


def group_by_parent(claims: Iterable[Claim]) -> dict[str, ParentGroup]:
    """Group claims by parent identifier.

    The helper should produce deterministic ordering and allow unit tests to
    validate aggregation behavior without running the entire pipeline.
    """

    grouped: dict[str, ParentGroup] = {}
    for claim in claims:
        group = grouped.setdefault(claim.parent_claim_core_id, ParentGroup(parent_id=claim.parent_claim_core_id))
        group.add_claim(claim)
    return dict(sorted(grouped.items(), key=lambda item: item[0]))
