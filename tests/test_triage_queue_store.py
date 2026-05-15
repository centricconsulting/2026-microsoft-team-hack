"""Failing tests for ITriageQueueStore — AC from US-013 (queue summary screen).

Gherkin AC reference: GitHub issue (queue summary screen — US-013)
Design reference:     Solutions Architect interface seam design, 2026-05-15

All tests are xfail(strict=True) — they MUST FAIL before the implementation PR.
Remove xfail decorators only once ALL of the following are committed:
    - InMemoryTriageQueueStore.save() implemented in infrastructure/triage_queue_store.py
    - InMemoryTriageQueueStore.list_classified() implemented
    - TriageService updated to accept ITriageQueueStore and call save() after ticket creation
    - GET /triage/queue route wired in api/main.py

Layer note: tests 1–6 instantiate InMemoryTriageQueueStore directly (infrastructure
contract tests). Test 7 uses AsyncMock(spec=ITriageQueueStore) to verify TriageService
behaviour — no concrete store is required.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock

from triage_assistant.application.interfaces import ITriageQueueStore
from triage_assistant.domain.models import (
    ClassifiedRequestSummary,
    HelpRequest,
    TriageCategory,
    TriagePriority,
    TriageResult,
)
from triage_assistant.infrastructure.triage_queue_store import InMemoryTriageQueueStore


# ─── Shared helpers ───────────────────────────────────────────────────────────

def _make_request(request_id: str, account_id: str = "DCI-001") -> HelpRequest:
    return HelpRequest(
        request_id=request_id,
        submitted_by="Marcus Webb",
        date_submitted="2026-03-10",
        subject="Export button broken on site status report",
        description="Nothing happens when I click Export to CSV.",
        account_id=account_id,
    )


def _make_result(
    classification: TriageCategory,
    confidence: float = 0.92,
    ticket_id: str = "TKT-001",
) -> TriageResult:
    return TriageResult(
        classification=classification,
        rationale="AI classification.",
        confidence=confidence,
        ticket_id=ticket_id,
    )


# ─── Shared fixture ───────────────────────────────────────────────────────────

@pytest.fixture
def store() -> InMemoryTriageQueueStore:
    return InMemoryTriageQueueStore()


# ─── AC-1: Results sorted High priority first ─────────────────────────────────
# Given classified requests exist in the store
# When the Triage Lead views the queue summary
# Then results are returned with High urgency requests first,
#      regardless of insertion order


async def test_list_classified_mixed_priority_returns_high_priority_first(
    store: InMemoryTriageQueueStore,
) -> None:
    # Arrange — save Normal-priority then High-priority
    await store.save(_make_request("REQ-N01"), _make_result("Data Patch", confidence=0.95))
    await store.save(_make_request("REQ-H01"), _make_result("Needs Human Review", confidence=0.75))

    # Act
    results = await store.list_classified()

    # Assert — High precedes Normal regardless of insertion order
    assert len(results) == 2
    assert results[0].priority == TriagePriority.high
    assert results[1].priority == TriagePriority.normal


# ─── AC-2: Filter by queue returns only that queue ────────────────────────────
# Given classified requests exist across multiple routing queues
# When the Triage Lead filters by a specific queue
# Then only requests assigned to that queue are returned, in urgency order


async def test_list_classified_filtered_by_queue_excludes_other_queues(
    store: InMemoryTriageQueueStore,
) -> None:
    # Arrange — one request per queue
    await store.save(_make_request("REQ-001"), _make_result("Data Patch"))
    await store.save(_make_request("REQ-002"), _make_result("Engineering Ticket"))
    await store.save(_make_request("REQ-003"), _make_result("Field Support"))

    # Act
    results = await store.list_classified(queue="Data Patch")

    # Assert
    assert len(results) == 1
    assert results[0].classification == "Data Patch"
    assert all(r.classification == "Data Patch" for r in results)


# ─── AC-3: Needs Human Review classification has High urgency ─────────────────
# Given a request is classified as Needs Human Review
# When it appears in the queue summary
# Then its priority is High so the Triage Lead can distinguish it visually


async def test_list_classified_needs_human_review_classification_has_high_priority(
    store: InMemoryTriageQueueStore,
) -> None:
    # Arrange
    await store.save(
        _make_request("REQ-HRV"),
        _make_result("Needs Human Review", confidence=0.80),
    )

    # Act
    results = await store.list_classified()

    # Assert
    assert len(results) == 1
    assert results[0].classification == "Needs Human Review"
    assert results[0].priority == TriagePriority.high


# ─── AC-4: Empty store returns empty list (no error) ─────────────────────────
# Given no classified requests have been saved yet
# When the queue summary is requested
# Then an empty list is returned — no exception, no error state


async def test_list_classified_empty_store_returns_empty_list(
    store: InMemoryTriageQueueStore,
) -> None:
    # Arrange — nothing saved

    # Act
    results = await store.list_classified()

    # Assert
    assert results == []


# ─── AC-5: Boundary — 200 classified requests handled without degrading ───────
# Given 200 classified requests exist
# When list_classified is called with limit=200
# Then all 200 are returned as valid ClassifiedRequestSummary instances


async def test_list_classified_two_hundred_requests_returns_all_within_limit(
    store: InMemoryTriageQueueStore,
) -> None:
    # Arrange
    for i in range(200):
        await store.save(
            _make_request(f"REQ-{i:04d}"),
            _make_result("Engineering Ticket"),
        )

    # Act
    results = await store.list_classified(limit=200)

    # Assert
    assert len(results) == 200
    assert all(isinstance(r, ClassifiedRequestSummary) for r in results)


# ─── AC-6: save() is idempotent on request_id ────────────────────────────────
# Given save() is called twice with the same request_id
# When list_classified is called
# Then only one record exists — no duplicate created


async def test_save_same_request_id_twice_does_not_create_duplicate(
    store: InMemoryTriageQueueStore,
) -> None:
    # Arrange
    req    = _make_request("REQ-DUP")
    result = _make_result("Field Support")

    # Act
    await store.save(req, result)
    await store.save(req, result)

    # Assert
    results = await store.list_classified()
    assert len(results) == 1
    assert results[0].request_id == "REQ-DUP"
