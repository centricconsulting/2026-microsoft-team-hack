"""TriageService — application-layer orchestrator for the DCI triage pipeline.

This module sits in the Application layer and is the only entry point called
by the API layer. It depends on domain models and interface abstractions only —
no AI framework, HTTP client, or infrastructure imports are permitted here.
Swapping Foundry for a different AI backend, or the helpdesk for a different
ticket system, requires no changes to this file.
"""
from __future__ import annotations

import logging

from triage_assistant.domain.models import HelpRequest, TriageResult
from triage_assistant.application.interfaces import (
    IHelpdeskClient,
    IRagService,
    ITriageAgent,
    ITriageQueueStore,
)

logger = logging.getLogger(__name__)


class TriageService:
    """Orchestrates the full triage pipeline for a single inbound HelpRequest.

    Pipeline stages:
        1. RAG search   — retrieve historically similar cases from RagService
        2. Classify     — send request + RAG context to the AI agent
        3. Confidence   — override to Needs Human Review if below threshold
        4. Ticket       — create a work item in the DCI helpdesk system

    All dependencies are injected as interfaces (ITriageAgent, IRagService,
    IHelpdeskClient) so the service remains testable without any live AI or
    HTTP calls.
    """

    def __init__(
        self,
        agent: ITriageAgent,
        rag: IRagService,
        helpdesk: IHelpdeskClient,
        confidence_threshold: float = 0.85,
        queue_store: ITriageQueueStore | None = None,
    ) -> None:
        """Inject all pipeline dependencies and the confidence threshold.

        Args:
            agent: AI agent that classifies a HelpRequest into a TriageCategory.
            rag: Semantic search service that retrieves similar historical cases.
            helpdesk: HTTP adapter that creates work items in the DCI helpdesk.
            confidence_threshold: Minimum confidence for a classification to be
                accepted as-is. Requests below this value are reclassified as
                Needs Human Review. Defaults to 0.85.
            queue_store: Optional store for persisting classified requests for the
                queue summary screen. Failures are non-fatal — the triage result
                is always returned to the caller even if save() raises.
        """
        self._agent = agent
        self._rag = rag
        self._helpdesk = helpdesk
        self._confidence_threshold = confidence_threshold
        self._queue_store = queue_store

    async def triage(self, request: HelpRequest) -> TriageResult:
        """Run the full triage pipeline and return a classified, ticketed result.

        Args:
            request: The inbound DCI support request to classify.

        Returns:
            TriageResult with classification, rationale, confidence, optional
            resolution/follow_up_question, TriageMeta, and the helpdesk ticket_id.
        """
        # Step 1: retrieve similar historical cases for grounding
        similar_cases = await self._rag.search(request.description)

        # Step 2: classify — agent applies routing rules + RAG context
        classification_result = await self._agent.classify(request, similar_cases)

        # Step 3: confidence gate — override to Needs Human Review if below threshold
        # The threshold value lives in config (passed in at construction);
        # the MECHANISM lives here in the application layer.
        if classification_result.confidence < self._confidence_threshold:
            classification_result = classification_result.model_copy(
                update={"classification": "Needs Human Review"}
            )

        # Step 4: create a work item in the DCI helpdesk system
        ticket_id = await self._helpdesk.create_ticket(request, classification_result)
        classification_result = classification_result.model_copy(update={"ticket_id": ticket_id})

        # Step 5: persist to the queue store for the summary screen (non-fatal).
        # A store outage must never prevent the triage result reaching the caller.
        if self._queue_store is not None:
            try:
                await self._queue_store.save(request, classification_result)
            except RuntimeError as exc:
                logger.warning("Queue store save failed for %s: %s", request.request_id, exc)

        return classification_result
