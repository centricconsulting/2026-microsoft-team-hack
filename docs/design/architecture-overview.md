# DCI Triage Assistant — Architecture Overview

This document captures the system architecture for the DCI Triage Assistant proof-of-concept. For the technology rationale behind each decision, see the ADR index at [docs/adr/README.md](../adr/README.md).

---

## Architectural Style

**Clean Architecture** — four concentric layers. The Dependency Rule is inviolable: inner layers never import outer layers.

```
┌──────────────────────────────────────────────────────┐
│  api/          FastAPI routes, lifespan wiring        │
│  ┌────────────────────────────────────────────────┐  │
│  │  infrastructure/   SK Kernel, RAG, Helpdesk    │  │
│  │  ┌──────────────────────────────────────────┐  │  │
│  │  │  application/   Use cases, interfaces    │  │  │
│  │  │  ┌────────────────────────────────────┐  │  │  │
│  │  │  │  domain/   Models, ROUTING_MAP     │  │  │  │
│  │  │  └────────────────────────────────────┘  │  │  │
│  │  └──────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

| Layer | Package | Dependencies |
|---|---|---|
| Domain | `triage_assistant.domain` | None — pure Pydantic models |
| Application | `triage_assistant.application` | Domain only; depends on ABCs (`IRagService`, `IHelpdeskClient`), never on concrete implementations |
| Infrastructure | `triage_assistant.infrastructure` | Application interfaces + MAF (Microsoft Agent Framework) + httpx |
| API | `triage_assistant.api` | FastAPI; wires all layers together via lifespan |

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            FastAPI Application                           │
│                                                                          │
│   POST /triage        GET /patterns        GET /health                  │
│        │                    │                                            │
│        ▼                    ▼                                            │
│  ┌─────────────────┐  ┌──────────────────┐                              │
│  │  TriageService  │  │  PatternService  │                              │
│  └────────┬────────┘  └────────┬─────────┘                              │
│           │                    │                                          │
│    ┌──────┴──────┐             │                                         │
│    │             │             │                                         │
│    ▼             ▼             ▼                                         │
│  ┌──────────┐ ┌──────────────────┐                                      │
│  │  RAG     │ │  MAF Agent       │                                      │
│  │  Service │ │  (client.        │                                      │
│  │          │ │   as_agent())    │                                      │
│  └────┬─────┘ └────────┬─────────┘                                      │
│       │                │                                                 │
└───────┼────────────────┼─────────────────────────────────────────────────┘
        │                │
        ▼                ▼
┌───────────────┐  ┌────────────────────────────────────────────────────┐
│  In-Memory    │  │          Azure AI Foundry                          │
│  VectorStore  │  │                                                    │
│  (50 records, │  │  Model: gpt-4o             (classification)        │
│  loaded at    │  │  Model: text-emb-3-small   (RAG embeddings)        │
│  startup)     │  │                                                    │
└───────────────┘  └────────────────────────────────────────────────────┘
        │
        │ (embeddings generated at startup from historical_data.json)
        ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         HelpdeskClient                                │
│         POST https://app-x2slazjwhcxuq.azurewebsites.net/api/tickets │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Request Data Flow

```
1. Caller                POST /triage
                         {request_id, submitted_by, date_submitted,
                          subject, description, account_id}
                              │
2. FastAPI               Pydantic validation (fail fast)
                         Missing required fields → classification=Needs Human Review
                         follow_up_question="Please provide: [missing fields]"
                              │
3. TriageService         Concatenate subject + description → query_text
                              │
4. RAGService            embed(query_text) via text-embedding-3-small
                         cosine_similarity(query_embedding, historical_store)
                         → top_3_cases = [(request, resolution, what_we_did), ...]
                              │
5. TriageService         Build chat messages:
                         [system]  classify_system.txt
                                   (routing rules + confidence threshold rules)
                         [user]    "Historical similar cases:\n{top_3_cases}\n\n
                                    Classify this request:\n{subject}\n{description}"
                              │
6. MAF Agent             agent.run(user_message,
                           options={"response_format": TriageResult})
                         → AgentResponse[TriageResult] → response.value
                         → TriageResult(classification, rationale, confidence,
                                        resolution, follow_up_question, meta)
                              │
7. TriageService         if result.confidence < settings.confidence_threshold (0.85):
                             result.classification = "Needs Human Review"
                             result.follow_up_question = (preserve LLM question or
                                                          "Confidence too low for auto-routing")
                              │
8. HelpdeskClient        POST /api/tickets
                         {submitted_by, subject, description,
                          suggested_resolution: result.resolution,
                          classification: result.classification,
                          assigned_team: ROUTING_MAP[result.classification]}
                         → ticket_id
                              │
9. FastAPI               Return TriageResult + ticket_id to caller
                         HTTP 200
```

---

## Key Interfaces (Seams)

These ABCs in `application/interfaces.py` are the seams that decouple the application from infrastructure. Either side can be swapped independently (e.g., replace `InMemoryVectorStore` with Azure AI Search, or replace `HelpdeskClient` with a mock in tests).

```python
class IRagService(ABC):
    async def load(self, path: str) -> None: ...
    async def search(self, query: str, top_k: int = 3) -> list[dict]: ...

class IHelpdeskClient(ABC):
    async def create_ticket(self, request: HelpRequest, result: TriageResult) -> str: ...
```

---

## Routing Map

```python
ROUTING_MAP = {
    "Data Patch":         "Damage Analytics Team",
    "Engineering Ticket": "Engineering Backlog",
    "Field Support":      "Field Support Desk",
    "Needs Human Review": "Triage Lead",
}
```

---

## Technology Stack

| Concern | Technology | Decision |
|---|---|---|
| Runtime | Python 3.13, uv | ADR-0001 |
| Web framework | FastAPI + uvicorn | ADR-0002 |
| AI orchestration | Microsoft Agent Framework (MAF) — `FoundryChatClient` + `client.as_agent()` | ADR-0003 |
| AI model | Azure AI Foundry gpt-4o + text-embedding-3-small | ADR-0003 |
| Vector store | In-memory (`FoundryEmbeddingClient` for embeddings) | ADR-0004 |
| HTTP client | httpx (async) | ADR-0001 |
| Configuration | pydantic-settings + dotenv | ADR-0001 |

---

## Extension Points

| Current (PoC) | Production upgrade |
|---|---|
| In-memory `IVectorStore` | Azure AI Search — connector swap, no Application layer change |
| File-based historical data (`historical_data.json`) | SQL Server via `IHistoricalCaseRepository` |
| Direct Azure OpenAI API key | Azure Key Vault + Managed Identity |
| Local uvicorn | Azure Container Apps |
| Single-step classification | MAF multi-agent pipeline (retrieve → classify → validate) |

---

## References

- [ADR-0001: Python Triage Architecture](../adr/ADR-0001-python-triage-architecture.md)
- [ADR-0002: API Framework](../adr/ADR-0002-api-framework.md)
- [ADR-0003: AI Orchestration](../adr/ADR-0003-ai-orchestration.md)
- [ADR-0004: Vector Store](../adr/ADR-0004-vector-store.md)
