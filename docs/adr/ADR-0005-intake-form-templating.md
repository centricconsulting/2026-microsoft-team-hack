# ADR-0005: Intake Form — HTML Templating Approach

**Status:** Accepted  
**Date:** 2026-05-13  
**Team:** Team Captain America

---

## Context

US-012 requires a user-facing intake form so that field contractors can submit support
requests without calling the JSON API directly. The form must be served by the existing
FastAPI application with no separate build pipeline, and must POST to the existing
`POST /triage` endpoint (whose request/response contract is locked by ADR-0001).

Three concerns must be resolved:

1. **How to render the HTML page** — inline Python string, Jinja2 template, or static file.
2. **How to submit the form** — HTML `<form>` POST (requires `python-multipart`, changes
   request encoding) or JavaScript `fetch()` posting JSON (no new server-side dependency,
   `POST /triage` unchanged).
3. **Where new code lives** — must respect the Dependency Rule; the form is a transport
   concern and must not bleed into the application or domain layers.

---

## Decision

We will add **Jinja2** as a dependency and serve the intake form via `Jinja2Templates`
mounted in `api/main.py` at `GET /`. The form will submit via a vanilla JavaScript
`fetch()` call posting `application/json` to the existing `POST /triage` endpoint,
preserving the API contract exactly as specified in ADR-0001.

---

## Considered Options

| Option | Brief Description |
|---|---|
| **A — Jinja2 template (chosen)** | Add `jinja2` dependency; serve `templates/intake.html` via `Jinja2Templates`; form submits JSON via `fetch()` |
| B — Inline `HTMLResponse` | No new dependency; return a multi-line HTML string from a new `GET /` route inside `main.py` |
| C — HTMX | Add HTMX CDN script; HTML form POSTs with HTMX attributes; server returns HTML fragments | 
| D — React/Vue SPA | Separate frontend build; served as static files; communicates with API | 

---

## Rationale

- **Chose Option A because:**
  - Keeps HTML in a dedicated file (`templates/intake.html`), preserving Separation of
    Concerns — the Python module does not contain embedded markup.
  - Jinja2 is the standard FastAPI templating library with first-class `Jinja2Templates`
    support and zero configuration overhead.
  - Using `fetch()` for JSON submission means `POST /triage` requires **zero changes** —
    no `python-multipart`, no form-encoding adapter, no API contract drift.
  - One new dependency (`jinja2`) for a clear architectural seam is a justified tradeoff.

- **Rejected Option B because:**
  - Embedding hundreds of lines of HTML as a Python string inside `main.py` violates
    Separation of Concerns and is unreadable in code review.
  - No structural improvement over Option A; the file-system separation Jinja2 provides
    is free once the library is present.

- **Rejected Option C because:**
  - HTMX requires the server to return HTML fragments from `POST /triage`, changing the
    response contract from JSON (`TriageResult`) to HTML — a violation of the locked
    API contract (ADR-0001) and of Separation of Concerns.
  - The classification logic should not know what presentation format the transport needs.

- **Rejected Option D because:**
  - Violates AC-4 (no separate JS build pipeline) and introduces a wholly separate
    technology layer with no proportionate benefit for a hackathon PoC.

---

## Data Contract Lock

The following are **unchanged** by this ADR. Any implementation that deviates from these
shapes must update ADR-0001 first.

**`HelpRequest` (POST /triage request body):**
```
request_id: str
submitted_by: str
date_submitted: str      # ISO 8601 (e.g. "2026-05-13")
subject: str
description: str
account_id: str
```

**`TriageResult` (POST /triage response body):**
```
classification: str      # "Data Patch" | "Engineering Ticket" | "Field Support" | "Needs Human Review"
rationale: str
confidence: float
resolution: str | None
follow_up_question: str | None
meta: TriageMeta | None
ticket_id: str | None
```

---

## Architecture Impact

| Layer | Change |
|---|---|
| **domain/** | None |
| **application/** | None — no new Protocol interfaces required |
| **infrastructure/** | None |
| **api/main.py** | Add `Jinja2Templates` mount + new `GET /` route |
| **api/templates/** | New directory; `intake.html` template |
| **pyproject.toml** | Add `jinja2>=3.1.0` dependency |

The form is a **transport concern** that lives entirely within the `api/` layer. The
Dependency Rule is not violated: `intake.html` has no Python imports, and `main.py`
already owns all composition-root responsibilities.

---

## Consequences

- ✅ Field contractors have a browser-addressable intake surface — closes the explicit
  challenge requirement.
- ✅ `POST /triage` is unchanged; existing consumers (e.g. `triage.http` test file,
  automated callers) continue to work without modification.
- ✅ No `python-multipart` dependency needed; form data is still transmitted as JSON.
- ✅ HTML lives in `templates/intake.html`, not embedded in Python code.
- ⚠️ Adds one new dependency (`jinja2`). This is the first non-API Python dependency
  in the `api/` layer.
- ⚠️ The form uses vanilla JS `fetch()`. If JavaScript is disabled, the form will not
  submit. Acceptable for a PoC; a `<noscript>` warning should be included.

---

## References

- [ADR-0001 — Python Triage Architecture](ADR-0001-python-triage-architecture.md) — API contract (HelpRequest / TriageResult)
- [ADR-0002 — API Framework](ADR-0002-api-framework.md) — FastAPI + uvicorn decisions
- [GitHub Issue #4 — US-012 Ticket Intake Form](https://github.com/centricconsulting/2026-microsoft-team-hack/issues/4)
- [FastAPI Jinja2 Templates docs](https://fastapi.tiangolo.com/advanced/templates/)
