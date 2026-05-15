# ADR-0002: API Framework — FastAPI

**Status:** Accepted  
**Date:** 2026-05-12  
**Team:** Team Captain America


---

## Context

The triage assistant needs an HTTP server that accepts `POST /triage` requests and returns a JSON classification response. The framework must support async I/O (SK kernel calls and httpx are both async), integrate naturally with Pydantic v2 (which we already use for request/response models), and be runnable locally with a single command in < 30 seconds.

---

## Decision

Use **FastAPI** with **uvicorn** as the ASGI server.

---

## Considered Options

| Option | Brief Description |
|---|---|
| A — FastAPI + uvicorn | Async Python web framework, Pydantic v2 native, auto OpenAPI docs |
| B — Flask + Gunicorn | Sync-first WSGI framework; async support via extensions |
| C — Azure Functions (HTTP trigger) | Serverless; adds deployment infrastructure; Python worker model |

---

## Rationale

- **Chose FastAPI (A):** Native Pydantic v2 integration means `HelpRequest` and `TriageResult` models are declared once and serve as both validation schemas and OpenAPI spec generators. `async def` route handlers compose directly with `await agent.run(...)` and `await httpx_client.post(...)`. Auto-generated Swagger UI at `/docs` is genuinely useful for judges to test all 10 sample requests interactively without writing a separate client.
- **Rejected Flask (B):** Flask's sync model requires `asyncio.run()` wrappers around every SK kernel call, adding complexity with no benefit. Flask's OpenAPI support requires a separate `flask-smorest` or `apiflask` dependency.
- **Rejected Azure Functions (C):** Correct for production; premature for a 4-hour POC. Local development requires Azure Functions Core Tools, a storage emulator, and function.json configuration — all irrelevant overhead. The HTTP trigger adds no value over a local uvicorn process for a demo.

---

## Consequences

- ✅ `uv run uvicorn triage_assistant.api.main:app --reload` is the full run command
- ✅ `/docs` (Swagger UI) and `/openapi.json` are available for free
- ✅ FastAPI lifespan context manager handles Agent Framework initialisation and RAG loading at startup
- ⚠️ FastAPI is not a Microsoft product — it is an industry-standard Python framework with no Microsoft dependency conflicts
- ❌ Replacing FastAPI with Azure Functions for production requires rewriting route handlers as Function triggers (hours, not days)

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic v2 FastAPI Integration](https://fastapi.tiangolo.com/tutorial/response-model/)
