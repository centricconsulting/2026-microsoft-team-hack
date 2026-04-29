# ADR-NNNN: [Short Title — What Was Decided]

**Status:** Proposed | Accepted | Superseded | Deprecated  
**Date:** YYYY-MM-DD  
**Team:** [Team Name]

---

## Context

_What is the problem or situation requiring a decision? Describe the forces at play — technical, business, or organizational. Keep this to 2–4 sentences._

Example: We need to classify incoming DCI help desk tickets automatically using AI. We evaluated several approaches for structuring the AI interaction and managing prompt context.

---

## Decision

_State the decision clearly in one sentence._

Example: We will use **Semantic Kernel** with a structured plugin to invoke Azure OpenAI and parse the triage response.

---

## Considered Options

| Option | Brief Description |
| -- | -- |
| Option A | _Describe approach A_ |
| Option B | _Describe approach B_ |
| Option C | _Describe approach C_ |

---

## Rationale

_Why was this option chosen over the others? Reference tradeoffs explicitly._

- **Chose Option A because:** ...
- **Rejected Option B because:** ...
- **Rejected Option C because:** ...

---

## Consequences

_What becomes easier, harder, or different as a result of this decision?_

- ✅ _Positive consequence_
- ✅ _Positive consequence_
- ⚠️ _Tradeoff or constraint introduced_
- ❌ _Something that is now harder or ruled out_

---

## References

- [Link to relevant docs, spike, or PR]
- [Link to routing_rules.md](../../data/routing_rules.md) — if the decision relates to classification logic
