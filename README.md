# Request Triage Assistant — Centric Microsoft Practice Hackathon 2026

## Background

Damage Control, Inc. (DCI) is the Marvel Universe's premier disaster-recovery and reconstruction firm. When the Avengers level a city block, Damage Control sends in the crews. But behind the cape-and-crayon chaos, DCI runs like any real enterprise: hundreds of support requests land in the help desk every week. Operations coordinators, field contractors, and city liaisons all submit tickets — and right now, support staff manually read every one and route it to the right team.

It's slow. It creates delays. Tickets get misrouted.

### Vision

The DCI technology team wants **AI-assisted triage** to automatically classify incoming support requests and route them to the right team — instantly, accurately, with clear reasoning.

You'll build a proof-of-concept the support team can evaluate. Your solution processes a structured help request, uses AI to classify and route it, and returns a decision with rationale.

Solutions must reflect **enterprise engineering fundamentals**: observable, testable, and structured using clean architecture and domain-driven design patterns.

---

## Challenge Description

Build a proof-of-concept API (or callable script) that uses AI to triage incoming DCI help desk tickets. Classify each ticket into one of these categories:

- 🗄️ **Data Patch** — data-only fixes; SQL INSERT/UPDATE/DELETE against a known table; no code change needed
- 💻 **Engineering Ticket** — bugs, regressions, feature requests; requires a developer and a work item
- 🎫 **Field Support** — standard service desk requests; portal access, certifications, how-to questions, contractor onboarding
- ⚠️ **Needs Human Review** — ambiguous or insufficient information; route to triage lead

The API also provides a model-generated rationale explaining the classification, a confidence score, and metadata for observability.

---

## API Specification

The API exposes a `/api/triage` endpoint that accepts POST requests.

### Request Body (JSON)

```json
{
  "request_id": "REQ0001",
  "submitted_by": "Marcus Webb",
  "date_submitted": "2026-03-10",
  "subject": "Export button broken on site status report",
  "description": "When I click the Export to CSV button on the Site Status report page, nothing happens. I've tried Chrome and Edge. This was working fine last week.",
  "account_id": "DCI-44201"
}
```

### Response Body (JSON)

```json
{
  "classification": "Engineering Ticket",
  "rationale": "The request describes a UI button that stopped functioning after previously working. This is consistent with a software regression and requires a developer to investigate and fix the application code.",
  "confidence": 0.94,
  "next_steps": ["Create engineering work item", "Link to originating ticket", "Assign to AppDev queue"],
  "follow_up_question": null,
  "meta": {
    "model": "gpt-4o",
    "tokens_used": 312,
    "timestamp": "2026-03-10T09:14:22Z"
  }
}
```

> When `classification` is `"Needs Human Review"`, `follow_up_question` contains a specific question to ask the requester.

---

## Assets

- [data/help_requests/sample_requests.json](data/help_requests/sample_requests.json) — 10 sample help requests with varying complexity
- [data/routing_rules.md](data/routing_rules.md) — definitions of the four routing targets
- [data/glossary.md](data/glossary.md) — common DCI domain terms
- [triage.http](triage.http) — REST Client file with all 10 sample requests pre-loaded (VS Code [REST Client extension](https://marketplace.visualstudio.com/items?itemName=humao.rest-client))
- [.env.example](.env.example) — environment variable template; copy to `.env` and fill in your Azure OpenAI credentials
- [TEAMS.md](TEAMS.md) — team assignments (published by facilitator before kickoff)
- [docs/judging-scorecard.md](docs/judging-scorecard.md) — detailed scoring rubric with point values per criterion
- [docs/adr/ADR-template.md](docs/adr/ADR-template.md) — Architecture Decision Record template

---

## Challenge Requirements

Teams must:

### 1. Build a solution that

- Uses AI tools/frameworks available on the Microsoft platform (e.g., Azure OpenAI, Semantic Kernel, Azure AI Foundry, etc.)
- Exposes a lightweight API or command-line tool that implements the spec above
- Accepts one or more help requests as input
- Returns a routing classification with rationale and confidence score

### 2. Apply enterprise architecture patterns

- Structure code using **Clean Architecture** or **Vertical Slice Architecture**
- Apply **DDD** concepts where appropriate (entities, value objects, use cases)
- Use **GitHub Copilot** to accelerate development — but own what you ship (encouraged, not required)

### 3. Add observability

- Log what was received, what was classified, and why
- Include the AI model response and confidence score in logs
- Bonus: wire up Azure Application Insights or equivalent for trace visualization

### 4. Handle edge cases

- Requests with missing or minimal descriptions
- Requests that could fit multiple categories
- Requests that are clearly out of scope

---

## Judging Criteria

| Area | Description |
| -- | -- |
| Functionality | Does it route correctly? Is the output useful? |
| Architecture | Does the code reflect clean architecture and DDD patterns? |
| Observability | Are AI decisions logged and explainable? |
| Reliability | Does it handle vague or malformed requests gracefully? |
| Collaboration | Was the work split among team members? |
| Innovation | Bonus for agents, multi-step chains, or creative UX |

See [docs/judging-scorecard.md](docs/judging-scorecard.md) for the full rubric with point values.

---

## Teams

Teams are pre-assigned and announced one week before Hack Day. Participants know their teammates in advance to coordinate roles, review the challenge brief, and set up environments ahead of time.

See [TEAMS.md](TEAMS.md) for the team roster (published by the facilitator before kickoff).

> **Facilitator note:** Publish team assignments at least one week before the event so participants can prepare. Include team name, members, and a link to this repository.

---

## Schedule

### Kickoff Meeting — One Week Before Hack Day

**Duration:** 1 hour  
**Purpose:** Introduce the hackathon, reveal teams, and clarify requirements.

📊 **[Kickoff Presentation](docs/Centric-Microsoft-Practice-Hackathon-2026-Kickoff.pptx)** _(facilitator: create before kickoff)_

| Activity |
| -- |
| Event overview and objectives |
| Team assignments reveal |
| Challenge requirements & judging criteria |
| Tech stack & environment setup |
| Q&A |

> **Facilitator note:** Participants should leave with their team roster, repository access, and clear success criteria. Encourage teams to set up dev environments before Hack Day.

---

### Hack Day — 4 Hours

| Time | Activity |
| -- | -- |
| 9:00 – 9:15 | **Kickoff** — Problem brief overview |
| 9:15 – 9:45 | **Team Planning** — Teams present architecture approach to a facilitator |
| 9:45 – 11:30 | **Sprint 1: Build** |
| 11:30 – 12:30 | **Sprint 2: Build & Polish** |
| 12:30 – 12:50 | **Team Demos** (~5–8 min each) |
| 12:50 – 1:00 | **Judging + Awards + Retrospective** |

---

## Getting Started

### Prerequisites

- VS Code with Dev Container extension
- Docker Desktop / Rancher / Colima (to run the dev container)
- Git
- GitHub Copilot access (encouraged)

### Development Environment Setup

1. Clone this repository
2. Open in VS Code
3. When prompted, click **"Reopen in Container"** or use the Command Palette → `Dev Containers: Reopen in Container`
4. Wait for the container to build

The dev container includes .NET 9, Azure CLI, and GitHub CLI.

### Project Structure

```text
.
├── .devcontainer/             # Dev container configuration
├── .env.example               # Environment variable template (copy to .env)
├── triage.http                # REST Client file — one-click API testing in VS Code
├── TEAMS.md                   # Team assignments (filled in by facilitator)
├── .github/
│   ├── agents/                # Copilot agent definitions (e.g., triage-reviewer)
│   ├── hooks/                 # Copilot agent lifecycle hooks
│   ├── instructions/          # Copilot coding instructions (.NET, C#)
│   └── skills/                # Copilot skill definitions
├── data/
│   ├── help_requests/         # Sample and historical DCI help desk ticket data
│   ├── routing_rules.md       # Classification category definitions
│   └── glossary.md            # Domain terminology
├── src/                       # Your solution goes here
├── tests/                     # Your tests go here
└── docs/
    ├── adr/                   # Architecture Decision Records
    │   └── ADR-template.md    # Blank ADR template
    └── judging-scorecard.md   # Detailed scoring rubric
```

---

## Technology Stack

Teams may use any Microsoft-supported language, runtime, and Azure services. Mix and match as your team sees fit.

| Layer | Recommended Options |
| -- | -- |
| **Language / Runtime** | C# (.NET 9+), TypeScript / JavaScript (Node.js), Python |
| **API** | ASP.NET Core Minimal API, Azure Functions (isolated worker) |
| **Architecture** | Clean Architecture, Vertical Slice Architecture |
| **Testing** | xUnit, Jest, pytest — use what fits your stack |
| **AI** | Azure OpenAI, Azure AI Foundry, Semantic Kernel |
| **Observability** | OpenTelemetry + Azure Monitor / Application Insights |

GitHub Copilot is encouraged to accelerate development but is not required.

---

## Tips

- Let **GitHub Copilot** help you scaffold architecture layers — it knows the patterns from Copilot instructions in `.github/instructions/` (C#/.NET focused; adapt as needed for your stack).
- Start with the classification/routing logic at the core of your solution, then build outward toward the API surface.
- Copy `.env.example` to `.env` and fill in your Azure OpenAI credentials before you write a single line of AI code.
- Open `triage.http` in VS Code (requires the [REST Client extension](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)) to test your `/api/triage` endpoint with all 10 sample requests in one click.
- Use the sample requests to test your classification logic early and often.
- The Aspire dashboard hint: set `OTEL_EXPORTER_OTLP_ENDPOINT=http://host.docker.internal:4317` if running inside a dev container.

---

Good luck, and happy hacking! 🚀
