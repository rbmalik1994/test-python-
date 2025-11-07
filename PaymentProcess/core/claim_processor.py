"""Claim retrieval and transformation helpers."""

from __future__ import annotations

from typing import Iterable, List, Literal

from ..data.models.claim import Claim, ParentGroup
from ..data.models.event import PaymentEvent
from ..data.models.over_under import OUSummary
from ..data.models.payment_center import PaymentCenterCache, PaymentCenterClaims, PaymentCenterType

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

    def __init__(self) -> None:
        self._last_source: str | None = None

    def fetch_claims(self, source: ClaimSource, payment_event: PaymentEvent) -> Iterable[Claim]:
        """Fetch claims from the configured repository.

        Implementations typically delegate to :class:`ClaimRepository`. Keep
        this method thin so tests can stub it easily. Repository helpers should
        bulk load MongoDB documents and use :meth:`Claim.model_validate` to
        return hydrated Pydantic models.
        """

        raise NotImplementedError

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

        raise NotImplementedError

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

        raise NotImplementedError


def group_by_parent(claims: Iterable[Claim]) -> dict[str, ParentGroup]:
    """Group claims by parent identifier.

    The helper should produce deterministic ordering and allow unit tests to
    validate aggregation behavior without running the entire pipeline.
    """

    raise NotImplementedError
