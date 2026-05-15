# Request Triage Assistant — Centric Microsoft Practice Hackathon 2026

## :high_brightness: Background

Damage Control, Inc. (DCI) is the Marvel Universe's premier disaster-recovery and reconstruction firm.
When the Avengers level a city block, Damage Control sends in the crews. But behind the cape-and-crayon
chaos, DCI runs like any real enterprise: hundreds of support requests land in the help desk every week.
Operations coordinators, field contractors, and city liaisons all submit tickets — and right now, support
staff manually read every one and route it to the right team.

It's slow. It creates delays. Tickets get misrouted.  Support staff is overwhelmed!

### Vision

The DCI technology team wants to use AI to improve operational efficiency and customer service.  They feel AI agents can **triage** incoming requests and **propose** solutions for the IT team to review.  The solution will need to validate and classify the support request, propose a solution based on historical solutions, and interface with DCI's existing support system.

---

## :mag_right: Challenge Description

You'll build a **proof-of-concept** the support team can evaluate. As DCI has an existing relationship with Microsoft, they have a strong preference for a **solution which leverages Microsoft AI technologies**.

DCI realizes time is tight, and you may not be able to get everything accomplished today.  Focus on how your solution can add immediate value for DCI and highlight extension points for growth.  You don't need to build everything - focus on doing a few things really well.

1. **Create a solution proposal.** You will need to create a concise pitch deck for DCI leadership which demonstrates your understanding of DCI's challenge, your recommended solution, and preliminary proposal (timeline, team structure, costs, etc.).  Use AI.
1. **Validate and classify the support ticket.** The classification must include the rationale for the classification.  
   - If the solution is unable to classify the ticket, you should get a human involved.  
   - If the ticket does not contain the required data, get a human involved.
   - The team will need to:
     - Determine how the request is first received (HTTP POST, Teams chat, Power BI form, email, file, etc.)
     - Determine the required fields.
1. **Create a work ticket item in DCI's helpdesk system.**  The endpoints will be provided beforehand.
1. **Suggest a team and resolution based on historical data.** The team suggestion must include a rationale. Given a collection of data (e.g., a directory of JSON files), the solution should suggest the appropriate team(s) (routing) and a potential solution for DCI support staff.

### Classification Categories

Classify each ticket into one of these categories:

- 🗄️ **Data Patch** — data-only fixes; SQL INSERT/UPDATE/DELETE against a known table; no code change needed
- 💻 **Engineering Ticket** — bugs, regressions, feature requests; requires a developer and a work item
- 🎫 **Field Support** — standard service desk requests; portal access, certifications, how-to questions, contractor onboarding
- ⚠️ **Needs Human Review** — ambiguous or insufficient information; route to triage lead

---

## :sparkles: Examples

### Support request

```json
{
  "request_id": "REQ0001",
  "submitted_by": "Marcus Webb",
  "date_submitted": "2026-03-10",
  "subject": "Export button broken on site status report",
  "description": "When I click the Export to CSV button on the Site Status report page, nothing happens. I've tried Chrome and Edge. This was working fine last week."
}
```

### Response

```json
{
  "classification": "Engineering Ticket",
  "rationale": "The request describes a UI button that stopped functioning after previously working. This is consistent with a software regression and requires a developer to investigate and fix the application code.",
  "confidence": 0.94,
  "resolution": "Create an engineering work item and assign to the AppDev team.",
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

## :books: Assets

### Repository

Additional information, ticket classifications, example requests, glossary, and routing rules:
**<https://github.com/centricconsulting/2026-microsoft-team-hack>**

### Local Assets

- [data/help_requests/sample_requests.json](data/help_requests/sample_requests.json) — 10 sample help requests with varying complexity
- [data/routing_rules.md](data/routing_rules.md) — definitions of the four routing targets
- [data/glossary.md](data/glossary.md) — common DCI domain terms
- [triage.http](triage.http) — REST Client file with all 10 sample requests pre-loaded (VS Code [REST Client extension](https://marketplace.visualstudio.com/items?itemName=humao.rest-client))
- [docs/adr/ADR-template.md](docs/adr/ADR-template.md) — Architecture Decision Record template

### DCI Helpdesk System

The live helpdesk system your solution must integrate with:

| Resource | URL |
| --- | --- |
| **Application** | <https://app-x2slazjwhcxuq.azurewebsites.net> |
| **OpenAPI Spec** | <https://app-x2slazjwhcxuq.azurewebsites.net/openapi/v1.json> |
| **Swagger UI** | <https://app-x2slazjwhcxuq.azurewebsites.net/swagger> |
| **Remote MCP Server** | <https://app-x2slazjwhcxuq.azurewebsites.net/mcp> |

---

## :medal_sports: Awards

| Area                       | Description                                                                                                                                                            |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Avengers Initiative Award  | Awarded to the team with the strongest overall solution across innovation, architecture, teamwork, execution, and presentation.                                       |
| Best Use of AI             | Awarded to the team that most effectively applied AI to solve the DCI challenge through intelligent reasoning, automation, recommendations, or agent-driven workflows. |
| Best Teamwork              | Awarded to the team that demonstrated exceptional cross-discipline collaboration, communication, and shared ownership throughout the hack.                             |
| Best UX                    | Awarded to the team that delivered the most intuitive, engaging, and user-friendly experience for support staff and end users.                                         |
| Most Advanced Architecture | Awarded to the team that designed the most technically sophisticated, scalable, and well-structured solution architecture using Microsoft technologies.                |

---

## :people_hugging: Teams

Teams are pre-assigned. Participants know their teammates in advance to coordinate roles, review the challenge brief, and set up environments ahead of time.

---

### Hack Day — ~4 Hours

| Time              | Activity                                                                                |
| ----------------- | --------------------------------------------------------------------------------------- |
| 10:15am – 10:30am | **Kickoff** — Problem brief overview                                                    |
| 10:30am - 2:00pm  | **Team Hack** — Teams collaborate on the solution proposal, design, and implementation. |
| T.B.D.            | Working Lunch                                                                           |
| 2:00 - 3:00pm     | **Final presentations.** Each team gets 5 minutes (strict time limit)                   |
| 3:00pm            | Go home!                                                                                |

---

## :tada: Getting Started

### Prerequisites

- VS Code with Dev Container extension
- Docker Desktop / Rancher / Podman / Colima (to run the dev container)
- Git
- GitHub Copilot access (encouraged)

### Development Environment Setup

1. Clone this repository
2. Open in VS Code
3. When prompted, click **"Reopen in Container"** or use the Command Palette → `Dev Containers: Reopen in Container`
4. Wait for the container to build

The dev container includes .NET 9, Azure CLI, and the GitHub CLI.

### Project Structure

```text
.
├── .devcontainer/             # Dev container configuration
├── triage.http                # REST Client file — one-click API testing in VS Code
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
```

---

## :robot: Technology Stack

Teams are encouraged to use Microsoft AI technologies.  However, teams may use any technology they feel is appropriate.

Teams should state why they made their technology choices.

GitHub Copilot is encouraged to accelerate development but is not required.

---

## :bulb: Tips

- Let **GitHub Copilot** help you scaffold architecture layers — it knows the patterns from Copilot instructions in `.github/instructions/` (C#/.NET focused; adapt as needed for your stack).
- Start with the classification/routing logic at the core of your solution, then build outward toward the API surface.
- Open `triage.http` in VS Code (requires the [REST Client extension](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)) to test your `/api/triage` endpoint with all 10 sample requests in one click.
- Use the sample requests to test your classification logic early and often.
- The Aspire dashboard hint: set `OTEL_EXPORTER_OTLP_ENDPOINT=http://host.docker.internal:4317` if running inside a dev container.

---

Good luck, and happy hacking! 🚀

<https://loop.cloud.microsoft/p/eyJ3Ijp7InUiOiJodHRwczovL2NlbnRyaWNjb25zdWx0aW5nbGxjLnNoYXJlcG9pbnQuY29tLz9uYXY9Y3owbE1rWW1aRDFpSVd4R2NVNVJSV3RmZEd0eGJtYzFlbFZNVEdOTVNHSlBVVUpxWlU5MmRrWlFjWGxUU1Y4d01WOXVUMDlRUTJWTVJFMUZXRkJUWVZCUFUyVTRkMkpUTURjbVpqMHdNVUZFVUVwUU4wOUNWRTlFTmpOU1UwUlZXa1paVlVNMFdrVktRVVJNVkU1WUptTTlKbVpzZFdsa1BURSUzRCIsInIiOmZhbHNlfSwicCI6eyJ1IjoiaHR0cHM6Ly9jZW50cmljY29uc3VsdGluZ2xsYy5zaGFyZXBvaW50LmNvbS86Zmw6L3IvY29udGVudHN0b3JhZ2UvQ1NQXzQwOGQ1YTk0LTNmNDktNGFiNi1hNzgzLTljZDQyY2I3MGIxZC9Eb2N1bWVudCUyMExpYnJhcnkvTG9vcEFwcERhdGEvVW50aXRsZWQubG9vcD9kPXcxZTU4NjIwYjFkZTQ0MTE0YjkyZmNkNTA3MTI2ZjQxMyZjc2Y9MSZ3ZWI9MSZuYXY9Y3owbE1rWmpiMjUwWlc1MGMzUnZjbUZuWlNVeVJrTlRVRjgwTURoa05XRTVOQzB6WmpRNUxUUmhZall0WVRjNE15MDVZMlEwTW1OaU56QmlNV1FtWkQxaUlXeEdjVTVSUld0ZmRHdHhibWMxZWxWTVRHTk1TR0pQVVVKcVpVOTJka1pRY1hsVFNWOHdNVjl1VDA5UVEyVk1SRTFGV0ZCVFlWQlBVMlU0ZDJKVE1EY21aajB3TVVGRVVFcFFOMGxNVFVwTlFqVmFRVFZEVWtFelUwdzJUa3RDV1ZOT05VRlVKbU05SlRKR0ptWnNkV2xrUFRFbVlUMU1iMjl3UVhCd0puQTlKVFF3Wm14MWFXUjRKVEpHYkc5dmNDMXdZV2RsTFdOdmJuUmhhVzVsY2laNFBTVTNRaVV5TW5jbE1qSWxNMEVsTWpKVU1GSlVWVWg0YWxwWE5UQmpiV3hxV1RJNWRXTXpWbk5rUjJ4MVdqSjRjMWw1TlhwaFIwWjVXbGhDZG1GWE5UQk1iVTUyWWxoNGFVbFhlRWRqVlRWU1VsZDBabVJIZEhoaWJXTXhaV3hXVFZSSFRrMVRSMHBRVlZWS2NWcFZPVEprYTFwUlkxaHNWRk5XT0hkTlZqbDFWREE1VVZFeVZrMVNSVEZHVjBaQ1ZGbFdRbEJWTWxVMFpESktWRTFFWkRoTlJFWkNVa1pDUzFWRVpGQlJiRkpRVWtSWmVsVnNUa1ZXVm5CSFYxWldSRTVHY0VaVGEwWkZWRVpTVDFkQkpUTkVKVE5FSlRJeUpUSkRKVEl5YVNVeU1pVXpRU1V5TWpNeU9UVTVOMlpqTFRnelpqUXRORFV4TWkwNVpEbGtMV1UzWWpjd05USmpZbVkyWXlVeU1pVTNSQSUzRCUzRCIsInIiOmZhbHNlfSwiaSI6eyJpIjoiMzI5NTk3ZmMtODNmNC00NTEyLTlkOWQtZTdiNzA1MmNiZjZjIn19>
