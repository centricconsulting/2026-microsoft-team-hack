---
description: Review a DCI Triage Assistant design or implementation for Clean Architecture compliance, Dependency Rule violations, and interface quality
argument-hint: "Paste code, interface definitions, a design doc, or list the file paths to review"
agent: agent
---

Review the following design or code against the DCI Triage Assistant architecture standards.

Ground the review in:
- [data/glossary.md](../../data/glossary.md) — check all names against ubiquitous language
- [README.md](../../README.md) — check the API schema matches the required contract
- [.github/instructions/python.instructions.md](../instructions/python.instructions.md)
- [.github/instructions/dev-principles.instructions.md](../instructions/dev-principles.instructions.md)

## Review Checklist

### Dependency Rule
- [ ] Domain layer: zero third-party AI/HTTP imports
- [ ] Application layer: imports Domain only (`typing.Protocol`, stdlib, pydantic models)
- [ ] Infrastructure: implements Protocol interfaces from Application — not the reverse
- [ ] API layer: FastAPI routing and DI wiring only; no business logic

### Interface Design
- [ ] Every external dependency is behind an interface
- [ ] Interface names come from `data/glossary.md`
- [ ] One responsibility per interface (ISP)
- [ ] Interfaces defined in Application, not Infrastructure

### API Contract
- [ ] Request matches `README.md` schema
- [ ] Response matches `README.md` schema
- [ ] `meta` includes `model`, `tokens_used`, `timestamp`

### Observability & Security
- [ ] Every AI call logged: model, token count, latency, result, confidence
- [ ] `async/await` throughout — no sync wrappers around async code
- [ ] No hardcoded secrets; all config via `TriageSettings` (`BaseSettings`)
- [ ] All inputs validated at the API boundary (FastAPI request model)
- [ ] AI responses parsed with `pydantic` `model_validate_json()` — no `eval()`

## Output Format

For each violation found:
- **Location**: file + line or interface name
- **Rule violated**: which checklist item
- **Severity**: Blocker | Warning | Suggestion
- **Fix**: specific, actionable change

## Design / Code to Review

{{input}}
