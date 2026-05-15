---
description: >
  Use when designing architecture, reviewing or writing code, implementing features, or
  evaluating technical scope. Covers YAGNI, SOLID, DRY, Separation of Concerns, the
  Dependency Rule, Fail Fast validation, and AI confidence thresholds. Apply to all
  decisions made by the solutions-architect, implementation, and product-owner agents.
---

# Software Development Principles

- **YAGNI** — Reject speculative features. Build for the known use case.
- **SOLID** — Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency
  Inversion. Flag violations in design reviews.
- **DRY** — But be careful: premature abstraction is worse than duplication.
  Two implementations first, abstraction second.
- **Separation of Concerns** — The triage classification logic does not care how a ticket
  arrives (HTTP, Teams, email). The transport is infrastructure; the classification is domain.
- **Dependency Rule** — Domain does not depend on infrastructure. If you see an Azure SDK
  import in a use case handler, that is a violation.
- **Fail Fast / Validate at Boundaries** — Validate at the API surface; trust inside the
  domain boundary. Do not re-validate deep in the call stack.
- **Confidence Thresholds** — The triage system must have an explicit threshold below which
  it escalates to a human. The default is **0.85**. This is a product decision, not a
  technical one — do not hardcode it.
