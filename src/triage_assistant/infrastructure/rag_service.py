"""RagService — semantic similarity search over historical DCI cases.

Uses azure-ai-inference AsyncEmbeddingsClient to generate embeddings via Azure AI Foundry
with DefaultAzureCredential, and pure-Python cosine similarity for vector search.
No external vector store infrastructure is required — everything runs in process memory.

Data flow (load_historical_cases):
    historical_data.json  →  embed each case  →  store (case dict, vector) pairs

Data flow (search):
    query string  →  embed query  →  cosine similarity vs stored vectors  →  top-k dicts

Implements IRagService so the Application layer never imports AI clients directly.
Swap this class for an AzureAISearchRagService behind the same interface to move to
a persistent, scalable vector store with no Application layer changes.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

# azure-ai-inference is a transitive dependency of agent-framework.
from azure.ai.inference.aio import EmbeddingsClient as AsyncEmbeddingsClient
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

from triage_assistant.application.interfaces import IRagService
from triage_assistant.config import TriageSettings


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Pure-Python cosine similarity — avoids a numpy dependency for the PoC."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0


class RagService(IRagService):
    """In-memory RAG service using Azure AI Foundry text-embedding-3-small.

    Implements IRagService so the Application layer never imports AI clients directly.
    Embedding endpoint is derived from foundry_models_endpoint or by stripping the
    /api/projects/<project> suffix from foundry_project_endpoint.
    """

    def __init__(self, settings: TriageSettings) -> None:
        # Derive the models inference endpoint:
        # Use explicit FOUNDRY_MODELS_ENDPOINT if set; otherwise derive from project endpoint.
        # Project endpoint format: https://<resource>.services.ai.azure.com/api/projects/<proj>
        # Models endpoint format:  https://<resource>.services.ai.azure.com/models
        if settings.foundry_models_endpoint:
            models_endpoint = settings.foundry_models_endpoint
        else:
            base = settings.foundry_project_endpoint.split("/api/projects")[0]
            models_endpoint = f"{base}/models"

        credential = (
            AzureKeyCredential(settings.foundry_api_key)
            if isinstance(settings.foundry_api_key, str) and settings.foundry_api_key
            else DefaultAzureCredential()
        )
        extra = {} if isinstance(settings.foundry_api_key, str) and settings.foundry_api_key else {"credential_scopes": ["https://cognitiveservices.azure.com/.default"]}
        self._client = AsyncEmbeddingsClient(
            endpoint=models_endpoint,
            credential=credential,
            **extra,
        )
        self._model = settings.embedding_deployment
        self._cases: list[dict] = []
        # Parallel list of embedding vectors — index matches self._cases
        self._vectors: list[list[float]] = []
        self._historical_data_path = settings.historical_data_path

    async def load_historical_cases(self) -> None:
        """Embed all historical cases at startup and store them in memory.

        Called once from the FastAPI lifespan handler so the embeddings API
        is only hit at boot, not on every request.
        """
        data_path = Path(self._historical_data_path)
        self._cases = json.loads(data_path.read_text(encoding="utf-8"))

        # Build a single text representation per case for embedding.
        # Historical data uses a 'request' field; HelpRequest uses subject+description.
        # Try 'request' first (historical_data.json format), fall back to subject+description.
        texts = [
            (
                c.get("request")
                or f"{c.get('subject', '')} {c.get('description', '')}".strip()
                or "unknown"
            )
            for c in self._cases
        ]

        # Batch-embed all cases in one API call — more efficient than one call per case.
        # EmbeddingsResult.data is a list of EmbeddingItem objects with .embedding: list[float]
        result = await self._client.embed(input=texts, model=self._model, input_type="text")
        self._vectors = [item.embedding for item in result.data if isinstance(item.embedding, list)]

    async def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Return the top-k most similar historical cases for the given query.

        Embeds the query, computes cosine similarity against all stored vectors,
        and returns the cases sorted by descending similarity.
        """
        if not self._vectors:
            # load_historical_cases() wasn't called or returned no data — fail gracefully
            return []

        # Embed the incoming query with the same model used at load time
        result = await self._client.embed(input=[query], model=self._model, input_type="text")
        embedding = result.data[0].embedding
        query_vector: list[float] = embedding if isinstance(embedding, list) else []

        # Rank all cases by cosine similarity to the query vector
        scored = [
            (_cosine_similarity(query_vector, vec), i)
            for i, vec in enumerate(self._vectors)
        ]
        scored.sort(reverse=True)

        return [self._cases[i] for _, i in scored[:top_k]]

