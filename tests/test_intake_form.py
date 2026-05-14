"""Tests for the DCI Triage Assistant ticket intake form — GET / route.

Implements the test-first (TDD) contract for GitHub Issue #4 (US-012).

Design reference: docs/adr/ADR-0005-intake-form-templating.md
AC reference:     https://github.com/centricconsulting/2026-microsoft-team-hack/issues/4
"""
import httpx

from triage_assistant.api.main import app


# ─── Transport helper ──────────────────────────────────────────────────────────
# httpx.ASGITransport sends HTTP requests directly to the ASGI app without
# triggering the lifespan startup sequence. This lets us test routes that
# do not depend on app.state (GET / and GET /health) in CI without real
# Azure credentials.
async def _get(path: str) -> httpx.Response:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        return await client.get(path)


# ─── Intake Form — GET / — happy path (AC-1) ──────────────────────────────────

async def test_get_intake_form_returns_200():
    """GET / returns HTTP 200 OK (AC-1: happy path reachable)."""
    response = await _get("/")
    assert response.status_code == 200


async def test_get_intake_form_content_type_is_html():
    """GET / Content-Type is text/html (AC-4: Python-native Jinja2 template)."""
    response = await _get("/")
    assert "text/html" in response.headers["content-type"]


# ─── Intake Form — HelpRequest field inputs present in HTML (AC-5) ────────────

async def test_get_intake_form_contains_request_id_input():
    """Form contains an input named request_id (AC-5: HelpRequest field coverage)."""
    response = await _get("/")
    assert 'name="request_id"' in response.text


async def test_get_intake_form_contains_submitted_by_input():
    """Form contains an input named submitted_by (AC-5)."""
    response = await _get("/")
    assert 'name="submitted_by"' in response.text


async def test_get_intake_form_contains_date_submitted_input():
    """Form contains an input named date_submitted (AC-5)."""
    response = await _get("/")
    assert 'name="date_submitted"' in response.text


async def test_get_intake_form_contains_subject_input():
    """Form contains an input named subject (AC-5)."""
    response = await _get("/")
    assert 'name="subject"' in response.text


async def test_get_intake_form_contains_description_input():
    """Form contains an input (textarea) named description (AC-5)."""
    response = await _get("/")
    assert 'name="description"' in response.text


async def test_get_intake_form_contains_account_id_input():
    """Form contains an input named account_id (AC-5)."""
    response = await _get("/")
    assert 'name="account_id"' in response.text


# ─── Intake Form — client-side validation (AC-2) ──────────────────────────────

async def test_get_intake_form_all_inputs_carry_required_attribute():
    """All 6 HelpRequest inputs carry the HTML required attribute (AC-2).

    Client-side validation must prevent submission before an API call is made.
    Exactly 6 fields are required: request_id, submitted_by, date_submitted,
    subject, description, account_id.
    """
    response = await _get("/")
    assert response.text.count("required") >= 6


# ─── Intake Form — JavaScript-disabled safety (ADR-0005 §Consequences) ────────

async def test_get_intake_form_contains_noscript_warning():
    """A <noscript> warning must be present.

    ADR-0005 explicitly calls out that the form submission relies on
    JavaScript fetch(). Users with JS disabled must see a message rather
    than a silent failure.
    """
    response = await _get("/")
    assert "<noscript>" in response.text


# ─── Regression — existing routes must not break ──────────────────────────────

async def test_health_route_unaffected_by_intake_form():
    """GET /health still returns 200 and {status: ok} after the form route is added.

    Not marked xfail — this must pass both before and after implementation.
    GET /health does not access app.state so it works without lifespan startup.
    """
    response = await _get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
