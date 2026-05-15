---
description: Refine a raw feature request into a well-formed user story with acceptance criteria, then create a GitHub Issue
argument-hint: "Paste the raw feature request or idea here"
agent: agent
tools: [read, search, github/issue_write]
---

You are acting as the DCI Product Owner. Refine the following feature request into a
production-ready user story.

Follow the instructions in [ba-methodology.instructions.md](../instructions/ba-methodology.instructions.md)
and ground all domain language in [data/glossary.md](../../data/glossary.md).

## Steps

1. Identify the **bounded context** and **primary persona** (use the stakeholder map from
   [dci-domain.instructions.md](../instructions/dci-domain.instructions.md))
2. Correct any language drift against the ubiquitous language
3. Write the user story in canonical form:
   `As a [persona], I want to [action] so that [business outcome].`
4. Write **at least three** Given/When/Then acceptance criteria scenarios:
   - Happy path
   - Boundary or edge case
   - Unhappy path or access control
5. Apply the INVEST checklist — flag any failures and suggest how to fix them
6. List any domain events this feature produces or consumes
7. Flag any cross-context dependencies and suggest the integration pattern

## Create GitHub Issue

After completing the refinement above, create a GitHub Issue on `centricconsulting/2026-microsoft-team-hack`
using the following format:

**Title:** `[<Bounded Context>] <user story action — one line>`

**Body:**
```
## User Story
As a [persona], I want to [action] so that [business outcome].

## Acceptance Criteria
### Scenario 1 — Happy Path
Given ...
When ...
Then ...

### Scenario 2 — Boundary / Edge Case
Given ...
When ...
Then ...

### Scenario 3 — Unhappy Path / Access Control
Given ...
When ...
Then ...

## Domain Events
- `EventName`

## Notes
- Bounded context: <name>
- INVEST flags (if any): <list or "None">
- Cross-context dependencies (if any): <list or "None">
```

## Feature Request

{{input}}
