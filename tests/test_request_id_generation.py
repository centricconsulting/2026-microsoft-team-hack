"""Tests for Issue #6 — server-side ULID generation for HelpRequest.request_id.

Gherkin AC reference: https://github.com/centricconsulting/2026-microsoft-team-hack/issues/6
Design reference:     docs/adr/ADR-0006-request-id-generation.md

All tests are xfail(strict=True) — they MUST FAIL before the implementation PR.
Remove xfail only once all three of the following changes are committed:
  - HelpRequest.request_id  → Optional[str] = None
  - TriageResult.request_id → Optional[str] = None  (echoes server-generated ID)
  - POST /triage handler    → stamps ULID before calling triage_service.triage()
                              and copies it onto the returned TriageResult
  - intake.html             → request_id input removed

Layer note: these are API-layer tests. The triage_service is replaced with an
AsyncMock so no live Azure credentials or AI calls are required.
"""
import httpx
import pytest
from unittest.mock import AsyncMock

from triage_assistant.api.main import app
from triage_assistant.domain.models import TriageResult


# ─── Shared fixtures / helpers ────────────────────────────────────────────────

def _make_triage_service_mock() -> AsyncMock:
    """Return an AsyncMock whose triage() resolves to a plain TriageResult.

    No request_id is set here — the API handler is responsible for generating
    and echoing the ULID (the behaviour under test).
    """
    mock = AsyncMock()
    mock.triage.return_value = TriageResult(
        classification="Engineering Ticket",
        rationale="Export button stopped working — regression.",
        confidence=0.94,
    )
    return mock


# Minimal valid body with NO request_id — this is the desired post-implementation
# contract.  Before implementation this body causes a 422 (field required).
_VALID_BODY_WITHOUT_ID: dict = {
    "submitted_by": "Marcus Webb",
    "date_submitted": "2026-03-10",
    "subject": "Export button broken on site status report",
    "description": (
        "When I click Export to CSV, nothing happens. Was working last week."
    ),
    "account_id": "DCI-44201",
}


async def _post_triage(body: dict, mock_service: AsyncMock) -> httpx.Response:
    """POST /triage with a mocked triage_service injected into app.state."""
    app.state.triage_service = mock_service
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        return await client.post("/triage", json=body)


# ─── Scenario 1 — Happy Path ──────────────────────────────────────────────────
# Given a POST to /triage with no request_id in the body
# When the request is processed
# Then the response is HTTP 200 and contains a non-null server-assigned request_id


@pytest.mark.asyncio
async def test_triage_without_request_id_returns_200_with_assigned_id():
    # Arrange
    mock_service = _make_triage_service_mock()

    # Act
    response = await _post_triage(_VALID_BODY_WITHOUT_ID, mock_service)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert data["request_id"] is not None
    assert data["request_id"] != ""


# ─── Scenario 2 — Uniqueness / Boundary ──────────────────────────────────────
# Given two support requests submitted consecutively with no request_id
# When both reach POST /triage
# Then each receives a distinct, non-colliding request_id


@pytest.mark.asyncio
async def test_triage_two_submissions_receive_distinct_request_ids():
    # Arrange
    mock_service = _make_triage_service_mock()

    # Act — two sequential POSTs; each should trigger independent ULID generation
    response_one = await _post_triage(_VALID_BODY_WITHOUT_ID, mock_service)
    response_two = await _post_triage(_VALID_BODY_WITHOUT_ID, mock_service)

    # Assert
    assert response_one.status_code == 200
    assert response_two.status_code == 200
    id_one = response_one.json()["request_id"]
    id_two = response_two.json()["request_id"]
    assert id_one is not None
    assert id_two is not None
    assert id_one != id_two


# ─── Scenario 3 — Client Tampering / Unhappy Path ────────────────────────────
# Given a caller submits a JSON body that includes a request_id field
# When the API processes the request
# Then the client-supplied value is ignored and the server-generated ID is used


@pytest.mark.asyncio
async def test_triage_client_supplied_request_id_is_overwritten():
    # Arrange — attacker or misconfigured client supplies their own ID
    mock_service = _make_triage_service_mock()
    body_with_id = {**_VALID_BODY_WITHOUT_ID, "request_id": "CUSTOM-ID-9999"}

    # Act
    response = await _post_triage(body_with_id, mock_service)

    # Assert — server-generated ULID is returned; client value is discarded
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] != "CUSTOM-ID-9999"
    assert data["request_id"] is not None


# ─── UI complement — request_id input removed from intake form ────────────────
# Given the intake form is loaded
# When the HTML is inspected
# Then no input named request_id is present (field was removed per ADR-0006)


@pytest.mark.asyncio
async def test_intake_form_does_not_expose_request_id_input():
    # Arrange / Act
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")

    # Assert — request_id input must be absent from the rendered form
    assert response.status_code == 200
    assert 'name="request_id"' not in response.text
