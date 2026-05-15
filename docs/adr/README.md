# Architecture Decision Records

This index lists all ADRs for the DCI Triage Assistant. Each ADR captures the context, decision, and trade-offs for a significant architectural choice.

Use [ADR-template.md](ADR-template.md) when adding a new decision.

---

| ADR | Title | Status | Summary |
|---|---|---|---|
| [ADR-0001](ADR-0001-python-triage-architecture.md) | Python Triage Architecture | Accepted | Overall PoC architecture: Python 3.13, FastAPI, Microsoft Agent Framework, Clean Architecture layers (`domain` / `application` / `infrastructure` / `api`) |
| [ADR-0002](ADR-0002-api-framework.md) | API Framework | Accepted | FastAPI over Flask and Azure Functions; async-native, Pydantic v2 integration, auto-generated Swagger UI |
| [ADR-0003](ADR-0003-ai-orchestration.md) | AI Orchestration | Accepted | Microsoft Agent Framework (`agent-framework>=1.3.0`) — official SK successor; `OpenAIChatClient` + `agent.run()` replaces Semantic Kernel |
| [ADR-0004](ADR-0004-vector-store.md) | Vector Store | Accepted | In-memory `list[list[float]]` + `AsyncOpenAI` embeddings for 50-record PoC; Azure AI Search is a one-adapter swap for production |


---

## Naming Convention

`ADR-NNNN-slug.md` — four-digit zero-padded sequence, kebab-case slug.

## Status Values

| Status | Meaning |
|---|---|
| `Proposed` | Draft — decision not yet made |
| `Accepted` | Decision made and in effect |
| `Superseded` | Replaced by a later ADR (link to successor) |
| `Deprecated` | No longer relevant |
