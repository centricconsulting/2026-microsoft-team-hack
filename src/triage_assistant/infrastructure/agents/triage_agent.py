"""TriageAgent — infrastructure adapter that classifies DCI support requests via Azure AI Inference.

Implements the ITriageAgent interface defined in the Application layer. This class owns
all AI wiring: it creates a ChatCompletionsClient pointed at the configured AI Services
multi-model endpoint, and exposes a single classify() method that the Application layer calls.

Authentication uses AzureKeyCredential when FOUNDRY_API_KEY is set (local dev / CI),
falling back to DefaultAzureCredential (Managed Identity in production).

Data flow:
    HelpRequest + similar_cases (from RagService)
        → _build_user_message()              — formats ticket fields + RAG context into a prompt
        → client.complete(messages)          — single async call to gpt-4o via AI Services
        → parse JSON from response content   — model returns structured JSON per classify_system.txt
        → TriageResult                       — classification, rationale, confidence, resolution,
                                               follow_up_question, and TriageMeta (model/tokens/timestamp)

Note: confidence thresholding and "Needs Human Review" override happen in TriageService
(Application layer), not here. This agent reports exactly what the model returns.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from azure.ai.inference.aio import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

from triage_assistant.application.interfaces import ITriageAgent
from triage_assistant.config import TriageSettings
from triage_assistant.domain.models import HelpRequest, TriageMeta, TriageResult

# System prompt lives in prompts/ — loaded once at module import so disk I/O
# doesn't happen per-request.
_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "classify_system.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


def _format_rag_context(similar_cases: list[dict]) -> str:
    """Render the top-k similar historical cases as a readable text block.

    This text replaces the {{rag_context}} placeholder in the system prompt
    so the model has concrete examples to ground its classification.
    """
    if not similar_cases:
        return "No similar historical cases found."
    lines: list[str] = []
    for i, case in enumerate(similar_cases, 1):
        lines.append(f"Case {i}:")
        lines.append(f"  Request: {case.get('description', case.get('request', 'N/A'))}")
        lines.append(f"  Resolution: {case.get('resolution', 'N/A')}")
        lines.append(f"  What we did: {case.get('what_we_did', 'N/A')}")
    return "\n".join(lines)


def _build_user_message(request: HelpRequest, rag_context: str) -> str:
    """Build the single user-turn message sent to the agent on every classification.

    The system prompt already holds the persona, routing rules, and format spec.
    This message supplies the ticket data and the RAG context for this specific call.
    Respond with JSON only — no markdown fences — so json.loads() works directly.
    """
    return (
        f"Historical context for grounding:\n{rag_context}\n\n"
        f"Classify this DCI support request. Respond with JSON only (no markdown).\n\n"
        f"Request ID: {request.request_id}\n"
        f"Account: {request.account_id}\n"
        f"Submitted by: {request.submitted_by}\n"
        f"Date: {request.date_submitted}\n"
        f"Subject: {request.subject}\n"
        f"Description: {request.description}\n\n"
        f'JSON schema: {{"classification": "Data Patch|Engineering Ticket|Field Support|Needs Human Review", '
        f'"rationale": "string", "confidence": 0.0-1.0, '
        f'"resolution": "string or null", "follow_up_question": "string or null"}}'
    )


class TriageAgent(ITriageAgent):
    """Azure AI Inference adapter for DCI support request classification.

    Construction creates a ChatCompletionsClient pointed at the AI Services
    multi-model endpoint. Uses AzureKeyCredential when FOUNDRY_API_KEY is set,
    falling back to DefaultAzureCredential for Managed Identity in production.
    Each classify() call is a single stateless chat completion — no conversation
    history is carried between requests.
    """

    def __init__(self, settings: TriageSettings) -> None:
        # Build the models inference endpoint — same path used by EmbeddingsClient.
        # Project endpoint: https://<resource>.services.ai.azure.com/api/projects/<proj>
        # Models endpoint:  https://<resource>.services.ai.azure.com/models
        base = settings.foundry_project_endpoint.split("/api/projects")[0]
        models_endpoint = f"{base.rstrip('/')}/models"

        # Prefer API key auth; fall back to DefaultAzureCredential (Managed Identity)
        if isinstance(settings.foundry_api_key, str) and settings.foundry_api_key:
            credential: AzureKeyCredential | DefaultAzureCredential = AzureKeyCredential(settings.foundry_api_key)
            extra: dict = {}
        else:
            credential = DefaultAzureCredential()
            extra = {"credential_scopes": ["https://cognitiveservices.azure.com/.default"]}

        self._client = ChatCompletionsClient(
            endpoint=models_endpoint,
            credential=credential,
            **extra,
        )

        # Store model name for classify() and TriageMeta.
        self._model = settings.chat_deployment

        # Inject routing rules into the system prompt once at construction time.
        routing_rules = Path(settings.routing_rules_path).read_text(encoding="utf-8")
        self._system_prompt = _SYSTEM_PROMPT.replace("{{routing_rules}}", routing_rules)

    async def classify(
        self,
        request: HelpRequest,
        similar_cases: list[dict],
    ) -> TriageResult:
        """Classify a HelpRequest using RAG context from similar historical cases.

        Args:
            request: The inbound DCI support request.
            similar_cases: Top-k cases from RagService, each a dict from
                           historical_data.json.

        Returns:
            TriageResult populated with classification, rationale, confidence,
            optional resolution / follow_up_question, and meta (model + tokens).
        """
        # 1. Build RAG context string from similar cases retrieved by RagService.
        rag_context = _format_rag_context(similar_cases)

        # 2. Compose the single user message — ticket data + grounding context.
        user_message = _build_user_message(request, rag_context)

        # 3. Call the model — single stateless chat completion.
        response = await self._client.complete(
            messages=[
                SystemMessage(content=self._system_prompt),
                UserMessage(content=user_message),
            ],
            model=self._model,
        )
        choice = response.choices[0]

        # 4. Parse the JSON the model was instructed to return.
        #    Strip markdown code fences if the model added them despite instructions.
        raw = (choice.message.content or "").strip()
        if raw.startswith("```"):
            raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data: dict = json.loads(raw)

        # 5. Extract token usage from the response metadata for observability.
        tokens_used: int = 0
        usage = getattr(response, "usage", None)
        if usage:
            tokens_used = getattr(usage, "total_tokens", 0) or 0

        # 6. Stamp classification metadata — model name, token count, UTC timestamp.
        meta = TriageMeta(
            model=self._model,
            tokens_used=tokens_used,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        return TriageResult(
            classification=data["classification"],
            rationale=data["rationale"],
            confidence=float(data["confidence"]),
            resolution=data.get("resolution"),
            follow_up_question=data.get("follow_up_question"),
            meta=meta,
        )

