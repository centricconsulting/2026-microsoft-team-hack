"""Application-layer interfaces (ports) — the seams between business logic and infrastructure.

Each interface here defines a capability the Application layer needs without
specifying how it is fulfilled. Concrete implementations live in
triage_assistant.infrastructure and are injected at startup by main.py.

This separation means:
- TriageService never imports httpx, agent-framework, or azure-ai-inference.
- Infrastructure adapters can be swapped (e.g. AzureAISearch replacing the
  in-memory RagService) with no changes to the Application layer.
- Tests can inject simple AsyncMock fakes without standing up real services.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from triage_assistant.domain.models import HelpRequest, TriageResult


class IRagService(ABC):
    """Port for semantic similarity search over historical DCI cases.

    Implemented by RagService (in-memory, azure-ai-inference embeddings).
    Replace with AzureAISearchRagService for a persistent, scalable vector store.
    """
    @abstractmethod
    async def load_historical_cases(self) -> None:
        """Embed historical cases and populate the vector store."""

    @abstractmethod
    async def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Return the top-k most similar historical cases."""


class IHelpdeskClient(ABC):
    """Port for creating work items in the DCI Helpdesk system.

    Implemented by HelpdeskClient (HTTP POST to app-x2slazjwhcxuq.azurewebsites.net).
    """
    @abstractmethod
    async def create_ticket(self, request: "HelpRequest", result: "TriageResult") -> str:
        """Create a work item in the DCI helpdesk system and return the ticket_id."""


class ITriageAgent(ABC):
    """Port for AI-powered classification of DCI support requests.

    Implemented by TriageAgent (Microsoft Agent Framework + Azure AI Foundry gpt-4o).
    Replace with any other agent implementation without touching TriageService.
    """
    @abstractmethod
    async def classify(
        self,
        request: "HelpRequest",
        similar_cases: list[dict],
    ) -> "TriageResult":
        """Classify a HelpRequest using RAG context and return a TriageResult."""
