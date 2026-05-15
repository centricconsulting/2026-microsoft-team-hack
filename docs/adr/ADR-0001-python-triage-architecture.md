# ADR-0001: DCI Triage Assistant — Python Architecture

**Status:** Accepted  
**Date:** 2026-05-12  
**Team:** Team Captain America

---

## Context

Damage Control, Inc. receives hundreds of support tickets per week. Staff manually classify and route every one into one of four queues: **Data Patch**, **Engineering Ticket**, **Field Support**, or **Needs Human Review**. This is slow, error-prone, and a bottleneck.

The goal is a proof-of-concept AI triage assistant that:
1. Accepts an inbound support request via HTTP POST
2. Classifies it using an LLM, with a confidence score and rationale
3. Suggests a resolution grounded in historical resolved cases (RAG)
4. Automatically creates a work item in the DCI helpdesk system
5. Escalates to human review when confidence < 0.85

---

## Decision

A **FastAPI** application orchestrated by **Microsoft Agent Framework**, backed by **OpenAI gpt-4o** for classification and **text-embedding-3-small** for RAG. Historical resolution data (`historical_data.json`, 50 records) is embedded at startup using `AsyncOpenAI` and stored in-process with pure-Python cosine similarity. The DCI helpdesk is integrated via an async `HelpdeskClient` abstraction.

Sub-decisions: [ADR-0002](ADR-0002-api-framework.md) (FastAPI), [ADR-0003](ADR-0003-ai-orchestration.md) (Agent Framework), [ADR-0004](ADR-0004-vector-store.md) (in-memory RAG), [ADR-0005](ADR-0005-openai-provider.md) (direct OpenAI).

---

## Considered Options

| Option | Brief Description |
|---|---|
| A — FastAPI + Agent Framework + In-Memory RAG | FastAPI, Microsoft Agent Framework, AsyncOpenAI embeddings, pure-Python cosine similarity |
| B — Azure Functions + direct `openai` SDK | Serverless HTTP trigger; no orchestration framework; infrastructure overhead |
| C — FastAPI + LangChain | Non-Microsoft orchestration framework |

**Chose A.** FastAPI has native Pydantic v2 integration, async support, and auto-generated Swagger docs. Microsoft Agent Framework is Microsoft's current recommended Python AI orchestration SDK. In-memory RAG needs zero infrastructure. LangChain (C) is non-Microsoft; Azure Functions (B) adds setup complexity irrelevant to a 4-hour PoC.

---

## Runtime Environment

| Concern | Value |
|---|---|
| Python | 3.13 (pinned via `.python-version`) |
| Package manager | `uv` with `hatchling` build backend |
| `requires-python` | `>=3.11,<3.14` |
| `[tool.uv] prerelease` | `allow` — required for `agent-framework` pre-release builds |

---

## Dependencies

| Package | Version | Role |
|---|---|---|
| `fastapi` | `>=0.115.0` | HTTP framework |
| `uvicorn[standard]` | `>=0.32.0` | ASGI server |
| `pydantic-settings` | `>=2.6.0` | Config from `.env` |
| `agent-framework` | `>=1.3.0` | AI orchestration (Microsoft Agent Framework) |
| `azure-ai-projects` | `>=1.0.0` | Azure AI Foundry project client (transitive via `agent-framework[foundry]`) |
| `azure-identity` | `>=1.19.0` | `DefaultAzureCredential` for Foundry auth (transitive) |
| `httpx` | `>=0.27.0` | Async HTTP client for `HelpdeskClient` |

Dev: `pytest>=8.3.0`, `pytest-asyncio>=0.24.0`, `pytest-cov>=5.0.0`

---

## Solution Structure

```
pyproject.toml                       # uv project definition
.python-version                      # 3.13
.env.example                         # Required env var template
src/
  triage_assistant/
    config.py                        # TriageSettings — pydantic-settings; SecretStr for keys
    domain/
      models.py                      # HelpRequest, TriageResult, TriageMeta,
                                     # TriageCategory, ROUTING_MAP
    application/
      interfaces.py                  # ITriageAgent, IRagService, IHelpdeskClient (ABCs)
      triage_service.py              # Use-case: RAG → classify → confidence gate → ticket
      pattern_service.py             # Root-cause pattern detection (stub)
    infrastructure/
      agents/
        triage_agent.py              # OpenAIChatClient → agent.run() — implements ITriageAgent
      kernel_setup.py                # Agent Framework client factory
      rag_service.py                 # AsyncOpenAI embeddings + pure-Python cosine similarity
      helpdesk_client.py             # httpx-based DCI helpdesk HTTP client
    api/
      main.py                        # FastAPI app, lifespan, routes — composition root
tests/
  test_triage_service.py
  test_rag_service.py
  test_helpdesk_client.py
data/
  glossary.md
  routing_rules.md
  help_requests/
    historical_data.json             # 50 resolved cases — RAG seed data
    sample_requests.json             # 10 test cases for judge evaluation
```

**Dependency Rule:** inner layers never import from outer layers. `domain/` has zero PyPI dependencies. `application/` depends on `domain/` and its own interfaces (ABCs) only — never on concrete infrastructure. `api/main.py` is the sole composition root.

---

## Architecture Layers

```
┌────────────────────────────────────────────────────────┐
│  API Layer          api/main.py                      │
│  FastAPI lifespan + route handlers                   │
│  Composition root — only place concrete types wire   │
├────────────────────────────────────────────────────────┤
│  Application Layer  triage_service.py                │
│  Use-case logic — depends on interfaces only         │
│  No AI framework imports. No infrastructure types.   │
├────────────────────────────────────────────────────────┤
│  Domain Layer       domain/models.py                 │
│  HelpRequest, TriageResult, TriageCategory           │
│  Zero PyPI dependencies                              │
├────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                │
│  triage_agent.py    FoundryChatClient / FoundryAgent │
│  rag_service.py     FoundryEmbeddingClient           │
│  helpdesk_client.py httpx                            │
└────────────────────────────────────────────────────────┘
```

---

## Data Flow: POST /triage

```
1. Caller          POST /triage  {request_id, submitted_by, date_submitted,
                                  subject, description, account_id}
                        │
2. FastAPI         Pydantic validation → HelpRequest
                        │
3. TriageService   concatenate subject + description → query_text
                        │
4. RagService      FoundryEmbeddingClient.get_embeddings(query_text)
                   cosine_similarity(query_vec, stored_vecs)
                   → top_3_cases: list[dict]
                        │
5. TriageService   build user_message(request, rag_context)
                        │
6. TriageAgent     agent.run(user_message)   ← Foundry-routed gpt-4o call
                   response_format=TriageResult → response.value
                   → TriageResult(classification, rationale, confidence, ...)
                        │
7. TriageService   if confidence < 0.85: classification = "Needs Human Review"
                        │
8. HelpdeskClient  POST helpdesk/tickets  (async)
                        │
9. FastAPI         return TriageResult JSON
```

---

## Configuration

`config.py` fields (read from `.env` via pydantic-settings):

| Variable | Required | Default | Description |
|---|---|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | ✅ | — | Azure AI Foundry project endpoint URL |
| `HELPDESK_API_KEY` | ✅ | — | DCI helpdesk auth key |
| `CHAT_DEPLOYMENT` | — | `gpt-4o` | Foundry model deployment name |
| `EMBEDDING_DEPLOYMENT` | — | `text-embedding-3-small` | Foundry embedding model name |
| `FOUNDRY_MODELS_ENDPOINT` | — | — | Foundry inference endpoint (for `FoundryEmbeddingClient`) |
| `FOUNDRY_AGENT_NAME` | — | — | Foundry PromptAgent name (Option B, production) |
| `FOUNDRY_AGENT_VERSION` | — | — | Foundry PromptAgent version (Option B, production) |
| `HELPDESK_BASE_URL` | — | `https://app-x2slazjwhcxuq.azurewebsites.net` | Helpdesk endpoint |
| `CONFIDENCE_THRESHOLD` | — | `0.85` | Minimum confidence before escalation |
| `HISTORICAL_DATA_PATH` | — | `data/help_requests/historical_data.json` | RAG seed data |

---

## API Contract

### POST /triage

**Request:**
```json
{
  "request_id": "REQ0001",
  "submitted_by": "Marcus Webb",
  "date_submitted": "2026-03-10",
  "subject": "Export button broken on site status report",
  "description": "When I click the Export to CSV button...",
  "account_id": "DCI-44201"
}
```

**Response (200):**
```json
{
  "classification": "Engineering Ticket",
  "rationale": "...",
  "confidence": 0.94,
  "resolution": "...",
  "follow_up_question": null,
  "meta": {"model": "gpt-4o", "tokens_used": 387, "timestamp": "2026-05-12T10:14:22Z"},
  "ticket_id": "TKT-8821"
}
```

### GET /health

Returns `{"status": "ok"}` — useful for smoke-testing.

---

## What Is In Scope

| Feature | Status |
|---|---|
| POST /triage with classification | ✅ |
| Confidence-based escalation to Needs Human Review | ✅ |
| RAG from historical_data.json (50 records) | ✅ |
| Helpdesk ticket creation | ✅ |
| GET /health | ✅ |
| Pattern detection (GET /patterns) | ⚠️ stub |
| Auth/authz on the triage API | ❌ extension point |
| Azure AI Search for vector storage | ❌ extension point |
| Teams/email inbound transport | ❌ extension point |

---

## Run Command

```bash
uv run uvicorn triage_assistant.api.main:app --reload
```

OpenAPI docs at `http://localhost:8000/docs`.

---

## Consequences

- ✅ Clean Architecture seams survive AI framework swaps — the orchestration layer is replaceable without touching Application or Domain
- ✅ Single `.env` with `FOUNDRY_PROJECT_ENDPOINT` + `HELPDESK_API_KEY` is the minimum config for the PoC
- ✅ In-memory RAG with zero external infrastructure — no Azure Search provisioning needed
- ✅ `uv sync` is the single setup command; `.venv` is fully reproducible
- ⚠️ `agent-framework` requires `prerelease = "allow"` in `[tool.uv]`
- ⚠️ In-memory RAG is lost on restart — re-generated in < 5s at startup (acceptable for PoC)
- ⚠️ No authentication on the triage endpoint — acceptable for a judged demo, not production
- ⚠️ Pattern detection (`PatternService`) is a stub — not implemented for the PoC

---

## Sub-ADRs

| ADR | Decision |
|---|---|
| [ADR-0002](ADR-0002-api-framework.md) | FastAPI over Flask and Azure Functions |
| [ADR-0003](ADR-0003-ai-orchestration.md) | Microsoft Agent Framework for AI orchestration |
| [ADR-0004](ADR-0004-vector-store.md) | In-memory + `FoundryEmbeddingClient` over Azure AI Search for PoC |
| [ADR-0005](ADR-0005-agent-framework-migration.md) | SK → Agent Framework migration detail |

---

## References

- [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [OpenAI Python SDK](https://platform.openai.com/docs/libraries/python-library)
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [uv — Python package manager](https://docs.astral.sh/uv/)
- [data/routing_rules.md](../../data/routing_rules.md)
- [data/glossary.md](../../data/glossary.md)
- [README.md](../../README.md)








