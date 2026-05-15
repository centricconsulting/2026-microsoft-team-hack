import pytest
from unittest.mock import AsyncMock

from triage_assistant.application.interfaces import ITriageQueueStore
from triage_assistant.domain.models import HelpRequest, TriageResult
from triage_assistant.application.triage_service import TriageService


@pytest.fixture
def agent():
    return AsyncMock()


@pytest.fixture
def rag():
    rag = AsyncMock()
    rag.search.return_value = []
    return rag


@pytest.fixture
def helpdesk():
    return AsyncMock()


@pytest.fixture
def service(agent, rag, helpdesk):
    return TriageService(agent, rag, helpdesk)


async def test_triage_calls_rag(service, agent, rag, helpdesk):
    request = HelpRequest(
        request_id="T-001",
        submitted_by="Test User",
        date_submitted="2026-01-01",
        subject="Test",
        description="Site 42 data is missing.",
        account_id="DCI-001",
    )
    agent.classify.return_value = TriageResult(
        classification="Engineering Ticket",
        rationale="Regression.",
        confidence=0.95,
    )
    helpdesk.create_ticket.return_value = "ticket-abc"

    result = await service.triage(request)

    rag.search.assert_called_once_with(request.description)
    helpdesk.create_ticket.assert_called_once()
    assert result.ticket_id == "ticket-abc"


# ─── AC-7: Queue store save failure does not prevent triage result being returned
# Given the queue store raises RuntimeError during save()
# When TriageService.triage() is called
# Then the classification result is still returned to the caller (save is non-fatal)


async def test_triage_queue_store_save_raises_does_not_propagate(
    agent: AsyncMock,
    rag: AsyncMock,
    helpdesk: AsyncMock,
) -> None:
    # Arrange
    queue_store = AsyncMock(spec=ITriageQueueStore)
    queue_store.save.side_effect = RuntimeError("store unavailable")

    # TriageService will need a queue_store parameter once implemented
    svc = TriageService(agent, rag, helpdesk, queue_store=queue_store)

    request = HelpRequest(
        request_id="REQ-STORE-FAIL",
        submitted_by="Maria Hill",
        date_submitted="2026-05-15",
        subject="Portal access denied for new contractor",
        description="Contractor DCI-EXT-009 cannot log in since yesterday.",
        account_id="DCI-44201",
    )
    agent.classify.return_value = TriageResult(
        classification="Field Support",
        rationale="Portal access issue for contractor.",
        confidence=0.91,
    )
    helpdesk.create_ticket.return_value = "TKT-999"

    # Act — must not raise even though queue_store.save() raises
    result = await svc.triage(request)

    # Assert — classification is returned; store failure is silently absorbed
    assert result.classification == "Field Support"
    assert result.ticket_id == "TKT-999"
    queue_store.save.assert_awaited_once()
