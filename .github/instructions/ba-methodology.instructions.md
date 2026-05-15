---
description: >
  Use when writing user stories, acceptance criteria, or requirements for DCI features.
  Covers BA templates (personas, user stories, INVEST), DDD patterns (ubiquitous language,
  bounded context, aggregates, domain events, CQRS, event sourcing, anti-corruption layer).
---

# BA & DDD Methodology

## BA Toolbox

### Personas

Before writing requirements, identify the persona who will use the feature.
A persona is not a job title — it is a role with a **goal, a pain point, and a context**:

```text
Persona: [Name / Role]
Goal: [What they are trying to accomplish]
Context: [When and where this happens, what system state they are in]
Pain: [What currently goes wrong or takes too long]
```

### User Stories

Write in the canonical form and always include the **why** — it constrains implementation:

```text
As a [persona], I want to [action] so that [business outcome].
```

Reject stories where the "so that" is "I can do the thing." That is circular.

### Acceptance Criteria

Write as **Given / When / Then** scenarios. One scenario per observable behaviour. Cover:

- Happy path
- Boundary conditions (empty, maximum, duplicate)
- Unhappy path (invalid input, system unavailable, low confidence score)
- Security / access control (who must NOT be able to do this)

### INVEST Checklist

Every story must be:
**I**ndependent · **N**egotiable · **V**aluable · **E**stimable · **S**mall · **T**estable.
If it fails any check, decompose or reframe it.

---

## DDD Toolbox

**Ubiquitous Language** — Use the exact terms from [data/glossary.md](../../data/glossary.md).
Never say "ticket" when the domain says "work order." Never say "user" when the domain says
"contractor" or "city liaison." Language drift = model drift.

**Bounded Context** — Every feature lives in exactly one context. If it does not, you have
discovered a seam that needs an explicit integration pattern (event, API contract,
anti-corruption layer).

**Aggregate** — Identify the consistency boundary. What must be transactionally consistent
together? Work orders belong to projects; certifications belong to contractors. An aggregate
root (e.g., `WorkOrder`, `Contractor`) owns its cluster.

**Domain Events** — Name the things that happened in past tense, using domain language:

- `WorkOrderCreated`, `WorkOrderClosed`, `ContractorOnboarded`, `SiteStatusChanged`,
  `ETLJobFailed`, `TriageClassificationProduced`

**CQRS** — Separate read and write models when the query shape diverges from the command
shape. Dashboard queries are reads. Creating a work order is a command. Do not conflate them.

**Event Sourcing** — Consider when audit trail and temporal queries matter (e.g., work order
history, billing disputes, contractor compliance history). Flag this to the Solutions
Architect early — it is a structural decision.

**Anti-Corruption Layer** — When integrating with the NYC City Damage Assessment API or other
external systems, define an ACL so the external model does not leak into the DCI domain model.

