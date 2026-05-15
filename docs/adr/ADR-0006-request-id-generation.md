# ADR-0006: Server-Side Generation of `request_id` Using ULID

**Status:** Accepted  
**Date:** 2026-05-15  
**Team:** Team Captain America  
**Resolves:** [GitHub Issue #6](https://github.com/centricconsulting/2026-microsoft-team-hack/issues/6)

---

## Context

`HelpRequest.request_id` is currently a required, user-supplied field exposed as an editable
text input on the intake form. This has three problems:

1. **Data quality** — users must invent or remember a unique identifier. Duplicates are not prevented by the domain model.
2. **UX burden** — field adds no value for the submitter; its purpose is system traceability, not user communication.
3. **Boundary violation** — identifier assignment is a system concern; it must not leak to the presentation layer.

The **Fail Fast / Validate at Boundaries** principle states that authoritative data must be
stamped at the API surface. The **Dependency Rule** prohibits the Domain model from depending
on any ID-generation infrastructure.

---

## Decision

`request_id` will be **generated server-side in the API layer** (`api/main.py`) using a
**ULID** (`python-ulid`, already a declared project dependency) immediately before `HelpRequest`
is constructed. The field is removed from the intake form. `HelpRequest.request_id` becomes
`Optional[str] = None`, populated exclusively by the API handler.

---

## Considered Options

| Option | Brief Description |
| -- | -- |
| A — ULID via `python-ulid` (chosen) | Generate at API boundary; lexicographically sortable; no new dependency |
| B — UUID4 via `uuid` (stdlib) | Generate at API boundary; random; non-sortable; 36 chars with dashes |
| C — Keep client-supplied ID | User types identifier; status quo; collision risk; UX burden |

---

## Rationale

- **Chose Option A (ULID)** because `python-ulid==3.1.0` is already installed. ULID is
  lexicographically sortable by creation time, URL-safe (26 alphanumeric chars), and the team
  already carries it as a dependency — using UUID4 alongside it would violate DRY.
- **Rejected Option B (UUID4)** because it produces a longer non-sortable string and adds no
  advantage over an already-present dependency.
- **Rejected Option C (client-supplied)** because it delegates a system-identity concern to
  the user, violates Fail Fast, and is the defect being corrected (Issue #6).

**Layer placement:** ID generation belongs in `api/main.py` (the composition root). The Domain
`HelpRequest` is a pure data container and must not own a generation strategy. Making
`request_id` optional preserves backward compatibility with all existing tests that construct
`HelpRequest` with an explicit ID.

---

## Consequences

- ✅ `request_id` is always unique, time-ordered, and system-assigned — no user action required
- ✅ Intake form loses one required field — fewer submission errors
- ✅ No new dependency — `python-ulid` is already declared in `pyproject.toml`
- ✅ Backward-compatible: `HelpRequest(request_id="explicit", ...)` still works in existing tests
- ⚠️ `HelpRequest.request_id` type changes from `str` (required) to `Optional[str] = None` — see ADR-0001 amendment below
- ⚠️ The ULID must be stamped **before** `HelpRequest` is passed to `TriageService` — `None`
  must never enter the application layer
- ❌ Clients that currently supply a `request_id` in the JSON body will have their value
  silently ignored — document in API release notes

---

## API Contract Changes (ADR-0001 Amendment)

### `HelpRequest` (request body)

| Field | Before | After |
| -- | -- | -- |
| `request_id` | `str` (required, user-supplied) | `Optional[str] = None` (server-generated ULID, stamped in API handler) |

### `TriageResult` (response body)

| Field | Before | After |
| -- | -- | -- |
| `request_id` | _(absent)_ | `Optional[str] = None` — echoes the server-generated ID back to the caller |

`TriageResult` must gain a `request_id` field so the intake form result panel
can display the assigned identifier (User Story AC #1). This is an additive,
non-breaking change — existing clients that ignore unknown fields are unaffected.
The field is `Optional` so unit tests that construct `TriageResult` directly
without a `request_id` remain valid.

---

## Implementation Sketch

```python
# api/main.py — POST /triage handler
from python_ulid import ULID

@app.post("/triage", response_model=TriageResult)
async def triage(request: HelpRequest) -> TriageResult:
    request.request_id = str(ULID())   # stamp before any downstream use
    ...
```

```html
<!-- intake.html — remove the request_id field block entirely -->
```

---

## References

- [GitHub Issue #6 — Auto-assign Request ID server-side](https://github.com/centricconsulting/2026-microsoft-team-hack/issues/6)
- [ADR-0001 — API contract (HelpRequest model)](ADR-0001-python-triage-architecture.md)
- [ADR-0002 — FastAPI handler patterns](ADR-0002-api-framework.md)
- [dev-principles.instructions.md — Fail Fast / Validate at Boundaries](../../.github/instructions/dev-principles.instructions.md)
- [`data/glossary.md`](../../data/glossary.md) — ubiquitous language reference
