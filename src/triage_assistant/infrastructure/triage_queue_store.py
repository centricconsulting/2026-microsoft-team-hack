"""InMemoryTriageQueueStore — in-memory implementation of ITriageQueueStore.

Stores classified requests in a dict keyed by request_id for O(1) idempotent
saves. Data lives in process memory and is lost on restart.

Production upgrade: replace with CosmosDbTriageQueueStore behind the same
ITriageQueueStore Protocol seam — no Application layer changes required.
"""
from __future__ import annotations

from triage_assistant.domain.models import (
    ClassifiedRequestSummary,
    HelpRequest,
    ROUTING_MAP,
    TriageCategory,
    TriagePriority,
    TriageResult,
)


class InMemoryTriageQueueStore:
    """In-memory queue store for the PoC.

    Implements ITriageQueueStore structurally (Protocol — no explicit inheritance).
    All records live in a dict keyed by request_id; duplicate saves overwrite
    rather than append, satisfying the idempotency contract.
    """

    def __init__(self) -> None:
        self._records: dict[str, ClassifiedRequestSummary] = {}

    async def save(self, request: HelpRequest, result: TriageResult) -> None:
        """Persist a classified request. Idempotent on request_id."""
        if not request.request_id:
            return

        priority = (
            TriagePriority.high
            if result.classification == "Needs Human Review"
            else TriagePriority.normal
        )
        summary = ClassifiedRequestSummary(
            request_id=request.request_id,
            subject=request.subject,
            submitted_by=request.submitted_by,
            date_submitted=request.date_submitted,
            classification=result.classification,
            assigned_team=ROUTING_MAP.get(result.classification, ""),
            priority=priority,
            confidence=result.confidence,
            ticket_id=result.ticket_id,
        )
        self._records[request.request_id] = summary

    async def list_classified(
        self,
        queue: TriageCategory | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ClassifiedRequestSummary]:
        """Return classified requests: High priority first, newest within each tier.

        Two-pass stable sort — pass 1 orders by date descending; pass 2 orders by
        priority ascending. Because sort() is stable, equal-priority records retain
        their date order from pass 1.
        """
        records = list(self._records.values())

        if queue is not None:
            records = [r for r in records if r.classification == queue]

        records.sort(key=lambda r: r.date_submitted, reverse=True)
        records.sort(key=lambda r: 0 if r.priority == TriagePriority.high else 1)

        return records[offset : offset + limit]
