# Documentation

## Contents

### Architecture Decision Records — [`docs/adr/`](adr/README.md)

| ADR | Summary |
|---|---|
| [ADR-0001](adr/ADR-0001-python-triage-architecture.md) | Overall PoC architecture — Python, FastAPI, Semantic Kernel, Clean Architecture |
| [ADR-0002](adr/ADR-0002-api-framework.md) | API framework — FastAPI + uvicorn |
| [ADR-0003](adr/ADR-0003-ai-orchestration.md) | AI orchestration — Semantic Kernel Python SDK |
| [ADR-0004](adr/ADR-0004-vector-store.md) | Vector store — SK InMemoryVectorStore |
| [ADR-template](adr/ADR-template.md) | Template for new decisions |

### API Reference — [`docs/api/`](api/triage-api.md)

- [triage-api.md](api/triage-api.md) — Endpoint reference: `POST /triage`, `GET /patterns`, `GET /health`; request/response schemas; classification categories; error codes

### Design — [`docs/design/`](design/architecture-overview.md)

- [architecture-overview.md](design/architecture-overview.md) — Clean Architecture layers, component diagram, request data flow, key interfaces, extension points

### Other

- [pitch-deck.md](pitch-deck.md) — Pitch deck content and talking points
