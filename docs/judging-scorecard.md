# Judging Scorecard — Centric Microsoft Practice Hackathon 2026

Judges use this scorecard to evaluate each team's demo. Scores are assigned per area; totals determine placement.

---

## Scoring Summary

| Area | Max Points |
| -- | --: |
| Functionality | 25 |
| Architecture | 20 |
| Observability | 15 |
| Reliability | 15 |
| Collaboration | 10 |
| Innovation | 15 |
| **Total** | **100** |

---

## Rubric

### 🎯 Functionality (25 pts)

_Does the solution do what was asked?_

| Score | Criteria |
| --: | -- |
| 21–25 | All 10 sample requests return correct classifications with clear rationale and a confidence score. `follow_up_question` is present on ambiguous tickets. Response shape matches the spec. |
| 14–20 | Most requests route correctly. Minor misclassifications (1–2) or incomplete response fields. |
| 7–13 | Partial functionality. Some requests route correctly; others are wrong or missing required fields. |
| 0–6 | Little to no correct routing. API may not run or crashes on several inputs. |

---

### 🏛️ Architecture (20 pts)

_Is the code structured well?_

| Score | Criteria |
| --: | -- |
| 17–20 | Clear separation of concerns. Domain logic is isolated from infrastructure. Use cases or command handlers are well-defined. Appropriate use of DDD concepts (entities, value objects, or aggregates). |
| 11–16 | Recognizable architecture pattern (Clean Architecture, Vertical Slice, etc.) with some blurring of boundaries. Core logic is identifiable. |
| 5–10 | Flat or service-class-heavy structure. Limited separation of concerns. Logic lives in controllers or a single file. |
| 0–4 | No discernible architecture. Everything in one class/file or framework scaffolding only. |

> Judges: review `src/` structure and ask teams to narrate their architecture in the demo.

---

### 🔭 Observability (15 pts)

_Can you see what the AI decided and why?_

| Score | Criteria |
| --: | -- |
| 13–15 | Structured logs include: request received, classification output, confidence score, model used, token count. Bonus: Azure Application Insights or Aspire dashboard wired up. |
| 8–12 | Key fields are logged but format is inconsistent or some fields are missing. |
| 3–7 | Console output or minimal logging present. Hard to trace a request through the system. |
| 0–2 | No logging or observability visible. |

---

### 🛡️ Reliability (15 pts)

_Does it handle bad inputs gracefully?_

| Score | Criteria |
| --: | -- |
| 13–15 | Handles vague requests (routes to `Needs Human Review` with a specific follow-up question). Handles malformed JSON and missing fields with a useful error response, not a crash. |
| 8–12 | Handles most edge cases. May crash or return a 500 on one or two unusual inputs. |
| 3–7 | Minimal error handling. Crashes or returns unhelpful errors on REQ0006 (vague ticket) or missing fields. |
| 0–2 | No error handling visible. |

---

### 🤝 Collaboration (10 pts)

_Was the work shared across the team?_

| Score | Criteria |
| --: | -- |
| 9–10 | All members contributed meaningfully. Demo narration involves multiple people. Roles were clearly divided (AI layer, API, tests, observability, etc.). |
| 6–8 | Most members contributed. One person may have dominated; others can speak to specific parts. |
| 3–5 | One or two members did most of the work. Others present but cannot explain their contribution. |
| 0–2 | Solo effort in practice, regardless of team size. |

> Judges: ask each team member a question about a specific part of the system during the demo.

---

### 💡 Innovation (15 pts)

_Did the team go beyond the minimum?_

| Score | Criteria |
| --: | -- |
| 13–15 | Notably creative extension: multi-step agent chain, suggested SQL scaffold in response, streaming classification, UI frontend, batch processing, or memorable DCI-themed detail. |
| 8–12 | One clear bonus feature beyond the spec (e.g., Application Insights wired up, retry logic, prompt tuning, a Copilot skill or agent used). |
| 3–7 | Attempted a bonus feature that is incomplete or minimally functional. |
| 0–2 | Spec-only solution with no extras. (Not penalized — just no bonus credit.) |

---

## Scoring Sheet

| Team | Functionality | Architecture | Observability | Reliability | Collaboration | Innovation | **Total** |
| -- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| Team 1 | | | | | | | |
| Team 2 | | | | | | | |
| Team 3 | | | | | | | |
| Team 4 | | | | | | | |

---

_Judges finalize scores after all demos. In the event of a tie, Innovation is the tiebreaker._
