import pytest
import respx
import httpx
from unittest.mock import MagicMock

from triage_assistant.infrastructure.helpdesk_client import HelpdeskClient
from triage_assistant.domain.models import HelpRequest, TriageResult, TriageMeta


@pytest.fixture
def settings():
    s = MagicMock()
    s.helpdesk_base_url = "https://helpdesk.example.com"
    return s


@pytest.fixture
def client(settings):
    return HelpdeskClient(settings)


@pytest.fixture
def sample_request():
    return HelpRequest(
        request_id="T-001",
        submitted_by="Marcus Webb",
        date_submitted="2026-03-10",
        subject="Export button broken",
        description="Nothing happens when I click Export.",
        account_id="DCI-001",
    )


@pytest.fixture
def sample_result():
    return TriageResult(
        classification="Engineering Ticket",
        rationale="Regression in UI.",
        confidence=0.94,
        resolution="Assign to AppDev team.",
    )


@respx.mock
async def test_create_ticket_posts_and_returns_id(client, sample_request, sample_result):
    respx.post("https://helpdesk.example.com/api/tickets").mock(
        return_value=httpx.Response(200, json={"ticket_id": "abc-123"})
    )
    ticket_id = await client.create_ticket(sample_request, sample_result)
    assert ticket_id == "abc-123"
