# DCI Intelligence Platform
### Centric Microsoft Practice Hackathon 2026

---

## SLIDE 1 — When Minutes Matter, Your Operations Can't Wait for a Ticket Queue

A contractor calls at 7am — locked out of the portal, crew standing by, site inspection due by noon. Someone has to stop what they're doing and fix it.

The ETL hasn't run in two days. There's a city council presentation tomorrow. A city liaison is about to walk in with stale data and no warning.

A contractor just got flagged non-compliant. His cert doesn't expire for three years. Someone entered the wrong year, and now he's pulled from the site.

You already know all of this. You handle it every week. Your team is good at it. That's not the problem.

The problem is that being good at handling it has hidden the cost of it.

---

## SLIDE 2 — The Best Ticket Is No Ticket At All

Every ticket represents a gap. ETL with no timeout. HR system that doesn't sync promotions. Import template with no validation. Someone resolves each one and moves on. The gap stays open.

The measure of success is not response time. It is ticket volume, trending down.

---

## SLIDE 3 — What We Built

**Classify** — Inbound request routed automatically with confidence score and rationale. Escalates to human below threshold.

**Resolve** — Matches to historical case. Recommends team and draft resolution. Surfaces what should have been done differently.

**Prevent** — Reads across the history. Names the gaps. Recommends closing them.

---

## SLIDE 4 — How We'd Build It

**Microsoft AI Stack**

| Component | Microsoft Product | Role |
|---|---|---|
| Agent orchestration | Azure AI Foundry + Microsoft Agent Framework | Classifies tickets, enforces confidence threshold, escalates to human below 0.85 |
| Semantic search | Azure AI Search | Matches inbound request to historical resolutions |
| Model | Azure OpenAI gpt-4o (via Foundry) | Classification, rationale generation, resolution drafts |
| Helpdesk integration | Existing DCI API (Azure App Service) | Creates work tickets, attaches resolution suggestions |

**Preliminary Proposal**

| Phase | Scope | Duration |
|---|---|---|
| 1 · Foundation | Classification MVP + helpdesk ticket creation | Weeks 1–4 |
| 2 · Resolution | RAG over historical data, team routing with rationale | Weeks 5–8 |
| 3 · Production | UAT, Azure Monitor observability, go-live | Weeks 9–12 |

| Role | FTE |
|---|---|
| Product Owner / Business Analyst | 1 |
| Solutions Architect | 1 |
| Developers | 2 |
| QA / DevOps | 1 |

**Estimated Azure cost at DCI ticket volume (~5,000 tickets / month)**

| Service | Est. Monthly |
|---|---|
| Azure OpenAI gpt-4o (classification + resolution drafts) | ~$150 |
| Azure AI Search (Standard S1) | ~$250 |
| Azure App Service (hosted API + helpdesk) | ~$140 |
| Azure Monitor / Application Insights | ~$30 |
| **Total** | **~$570 / month** |

---

## SLIDE 5 — How We Measure It

Remember that contractor from Slide 1? Now we measure how long he was blocked. The ETL? How often it recurs. The cert? Whether the alert fired before the crew was pulled.

| Metric | Direction |
|---|---|
| Ticket volume | Down |
| Contractor blocked time | Down |
| Recurrence rate | Down |
| Staff time on Tier-1 tasks | Down |

---

## SLIDE 6 — Where This Goes

**Auto-resolution** — Known problems resolved without a human. No queue touched.

**Auto-routing** — Ticket arrives at the right team with possible solutions already attached.

**Management recommendations** — Monthly: here are the five gaps, here is the fix, here is the cost of leaving them open.

**Predictive alerts** — Before the ETL fails. Before the cert expires. Before the import runs wrong.

---

## SLIDE 7 — The Question

Do the classifications match your expectation?
Do the patterns we found match what you already suspected?

If yes — 90 days to production.

---

Presented by: Team Captain America  
Microsoft Practice Hackathon 2026  
Microsoft Azure · Azure AI Foundry · Microsoft Agent Framework
