import pytest
from unittest.mock import AsyncMock

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
