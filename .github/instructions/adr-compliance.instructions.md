---
applyTo: "src/**,tests/**,docs/adr/**"
---

# ADR Compliance — Mandatory Pre-Implementation Step

**Before writing, editing, or reviewing any source file, you MUST read the ADRs.**

## Required Reading Order

1. [`docs/adr/ADR-0001-python-triage-architecture.md`](../../docs/adr/ADR-0001-python-triage-architecture.md) — authoritative source for:
   - Solution structure and layer boundaries
   - All Pydantic model field names and types (API contract)
   - Configuration field names and defaults
   - Data flow and component diagram
   - What is in scope for the POC
2. [`docs/adr/ADR-0002-api-framework.md`](../../docs/adr/ADR-0002-api-framework.md) — FastAPI + uvicorn decisions
3. [`docs/adr/ADR-0003-ai-orchestration.md`](../../docs/adr/ADR-0003-ai-orchestration.md) — AI orchestration decisions (MAF agent pattern, model selection)
4. [`docs/adr/ADR-0004-vector-store.md`](../../docs/adr/ADR-0004-vector-store.md) — InMemoryVectorStore and production upgrade path

## Rules

### Implementing
- Model field names, API request/response shape, and configuration keys in code MUST match the ADRs exactly — do not rename fields for style.
- If the ADR specifies a type (e.g., `SecretStr`, `float`, `Optional[str]`), use that type.
- If the ADR shows a default value (e.g., `confidence_threshold: float = 0.85`), use that default.
- Do not add fields to `HelpRequest` or `TriageResult` that are not in the ADR-0001 API contract without updating the ADR first.

### When Code and ADR Diverge
- If you implement something that differs from the ADR (structure, naming, behaviour), **update the ADR in the same step** — never leave them out of sync.
- Update the `Status` field of the ADR if the decision has been superseded.
- Add a changelog entry at the bottom of the relevant ADR noting what changed and why.

### When ADRs Are Missing
- If you are asked to implement a significant new capability (new endpoint, new service, new infrastructure integration) and no ADR exists for it, **write the ADR first** before producing code.
- Use the template at [`docs/adr/ADR-template.md`](../../docs/adr/ADR-template.md).

## Anti-Patterns (Do Not Do)

- Do not invent field names that differ from the ADR (`category` instead of `classification`, `suggested_resolution` instead of `resolution`).
- Do not change configuration key names without updating both the ADR and `.env.example`.
- Do not restructure `src/` without updating the Solution Structure section of ADR-0001.
- Do not add a new pip dependency without documenting it in the relevant ADR's Consequences section.
