# ADR-0004: Vector Store for RAG — In-Memory vs Azure AI Search

**Status:** Accepted  
**Date:** 2026-05-12 (revised 2026-05-13, 2026-05-15)  
**Team:** Team Captain America

---

## Context

The triage assistant uses RAG to ground resolution suggestions in historical resolved cases (`historical_data.json`, 50 records). A vector store is needed to store embeddings and perform similarity search at query time.

The choice must not require any external infrastructure provisioning during the 4-hour hackathon, but must have a clear upgrade path to a production-grade service.

---

## Decision

Use **in-memory storage with `azure.ai.inference.aio.EmbeddingsClient` (`AsyncEmbeddingsClient`) and pure-Python cosine similarity** for the POC. Embedding model: **`cohere-embed-v3-english`** (MaaS serverless model available on the Azure AI Services resource; no separate deployment required). Accept **Azure AI Search** as the production upgrade target.

---

## Considered Options

| Option | Brief Description |
|---|---|
| A — In-memory + `FoundryEmbeddingClient` | No infrastructure; data in process memory; pure-Python cosine similarity; `agent-framework[foundry]` for embeddings via Foundry endpoint |
| B — Azure AI Search (vector index) | Managed Azure service; persistent; scales to millions of records; Foundry-native vector index connector available |
| C — ChromaDB (embedded) | Open-source, file-backed; no external server; Python native; non-Microsoft |

---

## Rationale

- **Chose in-memory with `azure-ai-inference AsyncEmbeddingsClient` (A, revised):**
  - Zero infrastructure beyond the Foundry project endpoint already required for ADR-0003
  - 50 records fit in memory trivially; startup embedding takes < 5 seconds
  - Embeddings generated once at startup via `AsyncEmbeddingsClient` (`cohere-embed-v3-english` model, AI Services `/models` endpoint) and stored in a `list[list[float]]`
  - Pure-Python cosine similarity requires no numpy or external library
  - Aligns with the Hackathon Coordinator mandate to route all AI calls through Azure AI Foundry
  - `FoundryEmbeddingClient` (from `agent-framework`) was the original intent but shares the same RBAC constraint as `FoundryChatClient` (see ADR-0003). `azure-ai-inference` `AsyncEmbeddingsClient` with `AzureKeyCredential` achieves the same result without data-plane RBAC.
  - **`cohere-embed-v3-english`** is a serverless MaaS model available on the AIServices resource without a separate `az cognitiveservices account deployment create` step. The original `text-embedding-3-small` target was not deployed on the resource.
  - **`input_type="text"`** is required by the Cohere model; omitting it causes a `400 Bad Request` (`images must be used with input_type=image`). The Cohere-specific values `"search_document"` / `"search_query"` are rejected by this endpoint version.
  - Historical data (`historical_data.json`) uses a `request` field for the case text, not `subject` + `description`. `RagService.load_historical_cases()` reads `c.get("request")` first, falling back to `subject` + `description` for forward-compatibility with `HelpRequest`-formatted records.
  - The `IRagService` interface is the seam — swapping to Azure AI Search is an Infrastructure change only

- **Rejected Azure AI Search (B) for POC:**
  - Requires provisioning an Azure AI Search resource (S1 tier, ~$0.083/hour) and configuring a vector index — non-trivial setup time during a 4-hour hackathon
  - Overkill for 50 records
  - **This is the correct production choice** and should be wired in post-hackathon. Replace `RagService` with an `AzureAISearchRagService` behind the same `IRagService` interface — no Application layer changes required

- **Rejected ChromaDB (C):**
  - Non-Microsoft technology; conflicts with DCI's technology preference
  - Requires a separate Python dependency (`chromadb`) that is not part of the SK ecosystem
  - No clear Azure upgrade path within the Microsoft stack

---

## Production Upgrade Path

```python
# POC (rag_service.py) — in-memory, azure-ai-inference
from azure.ai.inference.aio import EmbeddingsClient as AsyncEmbeddingsClient
from azure.core.credentials import AzureKeyCredential

class RagService(IRagService):
    def __init__(self, settings: TriageSettings) -> None:
        base = settings.foundry_project_endpoint.split("/api/projects")[0]
        models_endpoint = f"{base}/models"
        self._client = AsyncEmbeddingsClient(
            endpoint=models_endpoint,
            credential=AzureKeyCredential(settings.foundry_api_key),
        )
        self._cases: list[dict] = []
        self._vectors: list[list[float]] = []

    async def load_historical_cases(self) -> None:
        # historical_data.json uses 'request' field; fall back to subject+description
        texts = [
            c.get("request") or f"{c.get('subject','')} {c.get('description','')}".strip()
            for c in self._cases
        ]
        result = await self._client.embed(
            input=texts, model="cohere-embed-v3-english", input_type="text"
        )
        self._vectors = [item.embedding for item in result.data]

    async def search(self, query: str, top_k: int = 3) -> list[dict]:
        result = await self._client.embed(
            input=[query], model="cohere-embed-v3-english", input_type="text"
        )
        # cosine similarity → return top-k

# Production — implement IRagService against Azure AI Search:
class AzureAISearchRagService(IRagService):
    def __init__(self) -> None:
        self._search_client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index_name,
            credential=AzureKeyCredential(settings.azure_search_api_key),
        )
```

Config additions required for Azure AI Search upgrade:

```env
AZURE_SEARCH_ENDPOINT=https://<resource>.search.windows.net
AZURE_SEARCH_API_KEY=<key>
AZURE_SEARCH_INDEX_NAME=dci-historical-cases
```

AI Services inference endpoint (shared with ADR-0003):

```env
FOUNDRY_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
FOUNDRY_API_KEY=<key>
EMBEDDING_DEPLOYMENT=cohere-embed-v3-english
```

---

## Consequences

- ✅ Zero infrastructure provisioning — hackathon team can start immediately
- ✅ Connector interface is identical to Azure AI Search — no application-layer changes for production upgrade
- ✅ `AzureKeyCredential` works without RBAC — consistent with ADR-0003 auth strategy
- ✅ `cohere-embed-v3-english` available serverless on the AIServices resource without explicit deployment
- ⚠️ In-memory store is lost on restart — embeddings are re-generated at startup (~5s for 50 cases, one batched API call). Acceptable for a demo
- ⚠️ `input_type="text"` is required for the Cohere model on this endpoint. Omitting it causes `400 Bad Request`
- ⚠️ Historical data field name is `request`, not `subject`/`description` — `RagService` handles both formats
- ⚠️ No persistence — cannot add new resolved cases to the store without restarting
- ❌ Not suitable beyond ~10k records (memory pressure); Azure AI Search upgrade required at scale

---

## References

- [azure-ai-inference Python SDK](https://learn.microsoft.com/en-us/azure/ai-services/reference/sdk-package-reference-python)
- [EmbeddingsClient — Azure AI Inference](https://learn.microsoft.com/en-us/python/api/azure-ai-inference/azure.ai.inference.embeddingsclient)
- [Azure AI Search Python SDK](https://learn.microsoft.com/azure/search/search-get-started-python)
- [data/routing_rules.md](../../data/routing_rules.md)
