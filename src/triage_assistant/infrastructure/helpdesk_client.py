"""Creates new DCI Helpdesk tickets that include the AI triage classification.

An inbound HelpRequest has no ticket until this client POSTs it. The ticket is
created with the original request details and the classification result together.
"""
import httpx

from triage_assistant.config import TriageSettings
from triage_assistant.application.interfaces import IHelpdeskClient
from triage_assistant.domain.models import HelpRequest, ROUTING_MAP, TriageResult


class HelpdeskClient(IHelpdeskClient):
    """Async adapter for the DCI Helpdesk API.

    API: https://app-x2slazjwhcxuq.azurewebsites.net
    POST /api/tickets → {"ticket_id": "<uuid>"}
    No authentication required.
    """

    def __init__(self, settings: TriageSettings) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.helpdesk_base_url,
            timeout=10.0,
        )

    async def create_ticket(self, request: HelpRequest, result: TriageResult) -> str:
        """POST /api/tickets with classification data; returns the new ticket_id."""
        payload = {
            "submitted_by": request.submitted_by,
            "subject": request.subject,
            "description": request.description,
            "suggested_resolution": result.resolution,
            "classification": result.classification,
            "assigned_team": ROUTING_MAP.get(result.classification, ""),
        }
        response = await self._client.post("/api/tickets", json=payload)
        response.raise_for_status()
        return response.json()["ticket_id"]

    async def aclose(self) -> None:
        await self._client.aclose()
