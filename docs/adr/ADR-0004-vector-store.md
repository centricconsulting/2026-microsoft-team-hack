# ADR-0004: Vector Store for RAG — In-Memory vs Azure AI Search

**Status:** Accepted  
**Date:** 2026-05-12  
**Team:** Team Captain America

---

## Context

The triage assistant uses RAG to ground resolution suggestions in historical resolved cases (`historical_data.json`, 50 records). A vector store is needed to store embeddings and perform similarity search at query time.

The choice must not require any external infrastructure provisioning during the 4-hour hackathon, but must have a clear upgrade path to a production-grade service.

---

## Decision

Use **in-memory storage with `FoundryEmbeddingClient` embeddings and pure-Python cosine similarity** for the POC. Accept **Azure AI Search** as the production upgrade target.

---

## Considered Options

| Option | Brief Description |
|---|---|
| A — In-memory + `FoundryEmbeddingClient` | No infrastructure; data in process memory; pure-Python cosine similarity; `agent-framework[foundry]` for embeddings via Foundry endpoint |
| B — Azure AI Search (vector index) | Managed Azure service; persistent; scales to millions of records; Foundry-native vector index connector available |
| C — ChromaDB (embedded) | Open-source, file-backed; no external server; Python native; non-Microsoft |

---

## Rationale

- **Chose in-memory with `FoundryEmbeddingClient` (A):**
  - Zero infrastructure beyond the Foundry project endpoint already required for ADR-0003
  - 50 records fit in memory trivially; startup embedding takes < 5 seconds
  - Embeddings generated once at startup via `FoundryEmbeddingClient` (text-embedding-3-small model, Foundry models endpoint) and stored in a `list[list[float]]`
  - Pure-Python cosine similarity (`sum(a*b for a,b in zip(...))`) requires no numpy or external library
  - Aligns with the Hackathon Coordinator mandate to route all AI calls through Azure AI Foundry
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
# POC (rag_service.py) — in-memory, pure Python
from agent_framework.foundry import FoundryEmbeddingClient
from azure.identity import DefaultAzureCredential

class RagService(IRagService):
    def __init__(self) -> None:
        self._embedding_client = FoundryEmbeddingClient(
            model=settings.embedding_deployment,
            endpoint=settings.foundry_models_endpoint,
            credential=DefaultAzureCredential(),
        )
        self._cases: list[dict] = []
        self._vectors: list[list[float]] = []

    async def search(self, query: str, top_k: int = 3) -> list[dict]:
        # embed query → cosine similarity → return top-k

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
```
AZURE_SEARCH_ENDPOINT=https://<resource>.search.windows.net
AZURE_SEARCH_API_KEY=<key>
AZURE_SEARCH_INDEX_NAME=dci-historical-cases
```

Foundry models endpoint (already required by ADR-0003 Foundry provider):
```
FOUNDRY_MODELS_ENDPOINT=https://<resource>.inference.ai.azure.com
FOUNDRY_EMBEDDING_MODEL=text-embedding-3-small
```

---

## Consequences

- ✅ Zero infrastructure provisioning — hackathon team can start immediately
- ✅ Connector interface is identical to Azure AI Search — no application-layer changes for production upgrade
- ⚠️ In-memory store is lost on restart — embeddings are re-generated at startup (~5s, 50 API calls batched). Acceptable for a demo
- ⚠️ No persistence — cannot add new resolved cases to the store without restarting (extension point: periodic reload)
- ❌ Not suitable beyond ~10k records (memory pressure); Azure AI Search upgrade is required at scale

---

## References

- [agent-framework FoundryEmbeddingClient](https://pypi.org/project/agent-framework/)
- [Azure AI Foundry — Inference Endpoints](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Azure AI Search Python SDK](https://learn.microsoft.com/azure/search/search-get-started-python)
- [data/routing_rules.md](../../data/routing_rules.md)
