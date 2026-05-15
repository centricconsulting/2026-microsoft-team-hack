# DCI Triage Assistant — Development Workflow

**Philosophy:** Shift left. Every defect caught after implementation costs more than one caught before it. Requirements ambiguity is a defect. A missing interface is a defect. An untestable acceptance criterion is a defect.

This document is the source of truth for how work flows from idea to done. It drives the prompts, skills, hooks, and instruction files under `.github/`.

---

## The Model

Two human decisions. Everything in between is autonomous.

```
User describes a request
        │
        ▼
  ┌─────────────┐
  │  PO INTAKE  │  PO creates a fully-formed, DoR-valid GitHub issue
  └──────┬──────┘  Issue is UNASSIGNED — sits in backlog
         │
         │  ◄── HUMAN: assign the issue when ready to prioritize it
         │
         ▼
  ┌──────────────────────────────────────┐
  │         AUTONOMOUS PIPELINE          │
  │                                      │
  │  1. SA     design branch, stubs, ADR │
  │      │                               │
  │  2. Test   failing tests PR merged   │
  │  Writer    against SA's stubs        │
  │      │                               │
  │  3. Impl   makes tests pass, CI green│
  │      │                               │
  │  4. PR     ready for review          │
  └──────┬───────────────────────────────┘
         │
         │  ◄── HUMAN: review PR and running behaviour
         │       approve → merge, issue closes
         │       request changes → pipeline resumes
         │       new discovery → new issues added to backlog
         ▼
       DONE — or new issues to prioritize
```

**The backlog is the prioritization surface.** Issues are created ready-to-assign. When you assign one, the pipeline starts. When you review the PR, you may close it, request changes, or create follow-up issues — which go back to the backlog unassigned.

**When the pipeline hits a genuine blocker** (ambiguous requirement, conflicting ADR, missing external dependency) the active agent unassigns the issue, labels it `status:blocked`, and comments the specific blocker. It does not guess.

**VS Code mechanism for autonomy: `handoffs` in `.agent.md` frontmatter.** Each agent file declares which agent it hands off to after completing its work. With `send: true`, the next prompt is auto-submitted — no human re-triggering needed. This is the native VS Code construct for the autonomous pipeline, not a workaround.

---

## Phase 1 — PO Intake

**Agent:** `product-owner`  
**Triggered by:** user describes a request (feature, bug, idea, retrospective action)  
**GitHub action:** PO creates a new issue — **unassigned, ready to assign immediately**

The issue must be DoR-valid before it is created. The PO does not create a draft issue and ask for review — it creates a finished issue that goes straight to the backlog. If the PO cannot make it DoR-valid (ambiguous request, missing domain context, conflicting bounded context) it asks the user one specific clarifying question before creating the issue.

**The PO:**
1. Reads `data/glossary.md` — all output uses canonical DCI terminology
2. Reads `.github/instructions/dci-domain.instructions.md` — confirms bounded context and stakeholder
3. Identifies the **persona**, the **domain event** produced or consumed, and the **out-of-scope boundary**
4. Self-validates DoR (checklist below) — if any item cannot be checked, asks the user before proceeding
5. Creates the GitHub issue with this body:

```markdown
## User Story
As a [persona], I want [capability], so that [business outcome].

## Bounded Context
<!-- Pick one. Full list in .github/instructions/dci-domain.instructions.md -->
[Incident Management | Work Order Management | Contractor Management | Site Management | Project Financials | Analytics & Reporting | External Integrations | Support Triage]

## Domain Event(s)
- [EventName] produced / consumed

## Acceptance Criteria

### Scenario: [happy path name]
Given [context]
When [action]
Then [outcome]

### Scenario: [failure / edge case name]
Given [context]
When [action]
Then [outcome]

## Out of Scope
- [explicit boundary]

## DoR Checklist (PO self-validated before issue was created)
- [x] Every scenario independently testable
- [x] Bounded context agreed
- [x] No unresolved external dependencies
- [x] Story completable in one session (~4 hours)
- [x] Domain language consistent with glossary
```

6. Adds label **`status:ready`** — the issue is ready to assign immediately

**The issue goes straight to `status:ready`.** There is no intermediate intake label. If you can see it in the backlog, it is ready to assign.

---

## Assigning an Issue — Starting the Pipeline

Assigning an issue to an agent or team is the signal that work should begin. The autonomous pipeline starts as soon as the issue is assigned.

**What to assign:** any issue with label `status:ready`  
**How to prioritize:** assign the highest-value issue; leave lower-priority issues unassigned in the backlog

Once assigned, the pipeline proceeds without further human input until a PR is ready for review — unless it hits a blocker (see below).

---

## Phase 2 — Design (Autonomous)

**Agent:** `solutions-architect`  
**Triggered by:** issue assigned (label `status:ready` + assignee set)  
**GitHub action:** SA opens branch `design/<issue-number>-<slug>`, label changes to `status:in-progress`

**The SA:**
1. Runs `Explore` agent to map existing code relevant to the story — writes a **codebase context comment** on the issue summarising what exists and what must not be duplicated
2. Identifies which **layer** owns the new code (domain / application / infrastructure / api)
3. Commits **interface stub file(s)** on the branch — real `.py` files with full type signatures and `...` bodies, zero implementation
4. Determines if an **ADR is required** — any new technology, structural pattern, or seam gets an ADR committed to `docs/adr/` on the same branch at `Accepted` status
5. Locks the **data contract** — if the story touches the API surface, schema changes are committed to `triage.http` or `README.md` on the same branch
6. Posts a design summary comment on the issue and **hands off to the test writer without waiting for human approval**:

```
Design complete — branch: design/<issue-number>-<slug>

Interface(s): src/triage_assistant/application/interfaces/<InterfaceName>.py
ADR: [None | docs/adr/ADR-XXXX-<title>.md]
Layer: [domain | application | infrastructure | api]
Data contract change: [None | see triage.http]

Handing off to test-writer.
```

**Blocker:** If the SA finds an ambiguity it cannot resolve (conflicting ADR, missing external dependency, requirement gap), it unassigns the issue, adds label `status:blocked`, and comments the specific question that must be answered before the pipeline can continue.

**SA does NOT produce implementation code.** If SA writes a method body, that is a violation.

---

## Phase 3 — Test Writing (Autonomous)

**Agent:** `test-writer`  
**Triggered by:** SA's design summary comment on the issue (no human gate)  
**GitHub action:** Test Writer opens branch `tests/<issue-number>-<slug>` and raises a **PR** with body `Part of #<issue-number>` (does **not** use `Closes` — the issue stays open until implementation)

**Test Writer:**
1. Reads the **Gherkin AC on the GitHub issue** — each `Scenario:` block becomes exactly one `pytest` test function
2. Reads the **SA's interface stub** — tests import the `Protocol`, never a concrete class
3. Writes **unit tests** using `pytest` + `pytest-asyncio`; mocks use `unittest.mock.AsyncMock` or `pytest-mock`
4. Runs `uv run pytest` locally — **all new tests must fail** before raising the PR. Include the failure output as a PR comment.
5. Marks failing tests with `@pytest.mark.xfail(strict=True, reason="implementation not yet written")`
6. Mocks are written against **interfaces only** — never against concrete classes or third-party SDKs directly

**Naming convention:** `test_<method>_<state_under_test>_<expected_behaviour>`

```python
@pytest.mark.asyncio
@pytest.mark.xfail(strict=True, reason="implementation not yet written")
async def test_classify_vague_description_returns_needs_human_review():
    """
    Scenario: vague description triggers human review
    Given a ticket with a one-sentence description and no specifics
    When the classifier processes it
    Then classification is Needs Human Review with a specific follow_up_question
    """
    mock_agent = AsyncMock(spec=ITriageClassifier)
    ...
```

**PR description template:**
```
Part of #<issue-number>

## Tests added
- [ ] Happy path: [scenario names]
- [ ] Edge cases: [scenario names]
- [ ] Failure scenarios: [scenario names]

## Confirmed failing
All new tests fail with `uv run pytest` on current `main`. Failure output:
[paste relevant pytest output]
```

**Output:**
- `[ ]` PR open (`tests/<issue-number>-<slug>` → `main`, `Part of #<issue>`)
- `[ ]` One test file per module under test (mirrors `src/triage_assistant/` under `tests/`)
- `[ ]` Happy path, edge case, and failure scenario tests
- `[ ]` All new tests confirmed failing (failure output in PR comment)
- `[ ]` Label `status:tests-written` applied to the issue after PR merges

---

## Phase 4 — Implementation (Autonomous)

**Agent:** `implementation`  
**Triggered by:** failing test PR merged (no human gate)  
**GitHub action:** Implementation agent opens branch `feat/<issue-number>-<slug>` and raises a **PR** with body `Closes #<issue-number>`; label changes to `status:in-review` when PR is ready

**Implementation agent MUST read before writing a single line of code:**
1. The **GitHub issue** — re-read the AC to understand the intended behaviour
2. The **SA's codebase context comment** on the issue — what exists, what must not be duplicated
3. **All relevant instruction files** in `.github/instructions/` (especially `python.instructions.md`)
4. **Existing tests** — these define exactly what to build
5. **Existing interface stubs** — implement the `Protocol`, do not redefine it
6. **Relevant ADRs** in `docs/adr/` — do not contradict an accepted decision

**Implementation agent builds to make tests pass — nothing more.**  
If an implementation decision cannot be resolved from the ADRs and issue context, it labels the issue `status:blocked`, comments the specific question, and stops.

**PR description template:**
```
Closes #<issue-number>

## What changed
[one paragraph — concrete classes added, wiring changed]

## Tests
- All previously-failing tests in `tests/<issue-number>-<slug>` now pass
- `uv run pytest` output: [paste relevant lines]

## Checklist
- [ ] Dependency Rule intact (no Domain/Application importing Infrastructure)
- [ ] Type hints on all public signatures
- [ ] No hardcoded secrets
- [ ] No new third-party imports in Domain or Application layers
```

**Output:**
- `[ ]` Draft PR open (`feat/<issue-number>-<slug>` → `main`, `Closes #<issue>`)
- `[ ]` Concrete class implementing the SA's `Protocol`
- `[ ]` All previously failing tests now pass (`uv run pytest` output in PR)
- `[ ]` No new third-party imports in Domain or Application layers
- `[ ]` Dependency Rule intact
- `[ ]` PR marked ready for review; label `status:in-review` applied to issue

---

## PR Review — The Human Checkpoint

**Triggered by:** implementation PR raised with label `status:in-review`  
**GitHub action:** human approves → squash merge → issue closes automatically → `status:done`

This is the single human gate in the pipeline. Review the PR and the running behaviour — not the intermediate design decisions.

**What to check:**
- [ ] `uv run pytest` is green (CI must have run)
- [ ] Run `uv run uvicorn triage_assistant.api.main:app --reload` and exercise the AC scenarios in `triage.http` — does each Gherkin scenario produce the expected output?
- [ ] No scope creep — the out-of-scope boundary on the issue was respected
- [ ] No hardcoded secrets or environment-specific values visible in the diff

**Outcomes:**
- **Approve** → squash merge, `feat: <story title> (#<issue-number>)`, issue closes, branch deleted
- **Request changes** → comment specifically on what must change; pipeline resumes autonomously
- **New discovery** → create new issues (they go to the backlog unassigned); merge or close the current PR on its own merits

**Do not block a PR because of future work.** If the code does what the issue asked, merge it. Future improvements are new issues.

---

## Artifact Registry

| Artifact | GitHub form | Created By | Triggers |
|---|---|---|---|
| User Story + Gherkin AC | Issue body (`status:ready`) | `product-owner` | Human assigns issue |
| Codebase context map | Issue comment | `Explore` + `solutions-architect` | Test writer picks up |
| Interface stub (`.py` Protocol) | Commit on `design/` branch | `solutions-architect` | Test writer picks up |
| ADR | Commit on `design/` branch | `solutions-architect` | Implementation picks up |
| Data contract (schema) | Commit on `design/` branch | `solutions-architect` | Test writer picks up |
| Failing test suite | PR (`tests/` branch, `Part of #N`) | `test-writer` | Implementation picks up |
| Production code | PR (`feat/` branch, `Closes #N`) | `implementation` | Human PR review |
| Follow-up issues | New issues (`status:ready`) | Any agent or human during review | Human assigns when prioritized |

---

## Agent Roster

| Agent | Role | Triggered by | Hands off to |
|---|---|---|---|
| `product-owner` | Issue creation | User request | `solutions-architect` via handoff |
| `solutions-architect` | Design, stubs, ADRs | Handoff from PO (issue assigned) | `test-writer` via handoff |
| `test-writer` | Failing tests | Handoff from SA | `implementation` via handoff |
| `implementation` | Production code | Handoff from test-writer | Human PR review |
| `Explore` | Codebase context | Subagent called by SA | SA reads the result |

**Autonomous chaining is implemented via `handoffs` in each `.agent.md` file.** When an agent completes its work it hands off to the next with `send: true` to auto-submit. The two human decisions (assign issue, review PR) are enforced by the pipeline design — not by blocking handoffs.

### Issue Labels

| Label | Meaning | Applied by |
|---|---|---|
| `status:ready` | Issue is DoR-valid, ready to assign | `product-owner` |
| `status:in-progress` | Pipeline running | `solutions-architect` on start |
| `status:in-review` | Implementation PR open | `implementation` |
| `status:blocked` | Pipeline stopped — needs human input | active agent |
| `status:done` | PR merged, issue closed | auto (GitHub) |
| `needs-human-review` | AI triage confidence below threshold | AI pipeline |

---

## Python Tech Stack Reference

This project is **Python 3.13** with `uv` as the package manager. The following are the mandated patterns — implementation and SA agents must not deviate without an ADR.

### Package Management
```bash
uv sync              # install all deps from pyproject.toml
uv add <package>     # add a dependency
uv run pytest        # run tests inside the venv
uv run uvicorn triage_assistant.api.main:app --reload  # run the API
```

### Layer Conventions

| Layer | Location | Allowed imports | Forbidden |
|---|---|---|---|
| Domain | `src/triage_assistant/domain/` | stdlib + `pydantic.BaseModel` | Any third-party AI/HTTP SDK |
| Application | `src/triage_assistant/application/` | Domain + `typing.Protocol` | Infrastructure, FastAPI, OpenAI |
| Infrastructure | `src/triage_assistant/infrastructure/` | Application interfaces + any SDK | Direct domain mutation |
| API | `src/triage_assistant/api/` | Application + FastAPI | Direct infrastructure calls bypassing application |

### Interfaces — Use `Protocol`
```python
# application/interfaces.py
from typing import Protocol
from triage_assistant.domain.models import HelpRequest, TriageResult

class ITriageAgent(Protocol):
    async def classify(self, request: HelpRequest) -> TriageResult: ...
```
No inheritance from `ABC`. `Protocol` enables structural subtyping — concrete classes do not need to import the interface.

### Data Models — Use `pydantic`
```python
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class HelpRequest(BaseModel):         # domain DTO
    request_id: str
    subject: str
    description: str

class TriageSettings(BaseSettings):   # config — reads from .env
    openai_api_key: SecretStr
    confidence_threshold: float = 0.85
    model_config = SettingsConfigDict(env_file=".env")
```

### Async — Always `async/await`
```python
# All service methods are async. No sync wrappers around async code.
async def classify(self, request: HelpRequest) -> TriageResult:
    response = await self._agent.run(user_message)
    return self._parse(response.text)
```

### MAF Agent Pattern
```python
from agent_framework import OpenAIChatClient

client = OpenAIChatClient(
    model=settings.chat_deployment,
    api_key=settings.openai_api_key.get_secret_value(),
)
agent = client.as_agent(name="...", instructions=system_prompt)
response = await agent.run(user_message)
# response.text may be wrapped in ```json fences — strip before parsing
```

**Agent design rule:** One concern per agent. An agent that classifies does not also suggest resolutions. If an agent's `instructions` string exceeds ~300 words, it probably has more than one concern.

### Testing Pattern
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_classify_low_confidence_returns_needs_human_review():
    mock_agent = AsyncMock(spec=ITriageAgent)
    mock_agent.classify.return_value = TriageResult(
        classification="Needs Human Review",
        confidence=0.72,
        ...
    )
    service = TriageService(agent=mock_agent, rag=AsyncMock())
    result = await service.process(low_detail_request)
    assert result.classification == "Needs Human Review"
    assert result.follow_up_question is not None
```

### Configuration — Never Hardcode
```python
# Good
settings = TriageSettings()  # reads from .env at startup

# Bad
client = OpenAIChatClient(api_key="sk-...")  # hardcoded secret
```

Validate required config at startup via FastAPI lifespan — fail fast, not at request time.

---

## VS Code Customization Construct Map

Each file in `.github/` maps to a specific VS Code Copilot construct with different behaviour. Using the wrong construct is common and breaks the intended workflow.

| VS Code Construct | Location | Loaded | Use for |
|---|---|---|---|
| **Workspace instructions** | `.github/copilot-instructions.md` | Always-on, every request | Repo-wide rules (e.g. no `rm`, recycle bin policy) |
| **File instructions** | `.github/instructions/*.instructions.md` | When `applyTo` pattern matches | Language/framework coding standards |
| **Prompt files** | `.github/prompts/*.prompt.md` | Manually via `/command` | Repeatable single tasks (write-adr, refine-story, review-ticket) |
| **Skills** | `.github/skills/<name>/SKILL.md` | Auto-loaded when relevant OR via `/command` | Multi-step reusable capabilities with optional scripts (Explore, scaffold-usecase) |
| **Agents** | `.github/agents/*.agent.md` | Selected from dropdown; chain via `handoffs` | Persistent personas with tool restrictions and pipeline handoffs |
| **Hooks** | `.github/hooks/*.json` | Deterministic at lifecycle events | Shell enforcement — run tests, block dangerous commands, audit tool calls |

### Handoff Pattern (autonomous pipeline)

Each agent `.agent.md` file declares its handoff target in YAML frontmatter:

```yaml
---
name: product-owner
handoffs:
  - label: Hand off to Solutions Architect
    agent: solutions-architect
    prompt: "The issue is created and DoR-valid. Please begin design for issue #{{issue_number}}."
    send: true
---
```

`send: true` auto-submits the prompt — the next agent starts without human re-triggering. This is the VS Code-native mechanism for the autonomous pipeline.

### Hooks vs Instructions vs Skills

- **Instructions** guide the AI about _what_ to produce. The AI can ignore them.
- **Skills** guide the AI about _how_ to perform a complex task. Loaded on-demand.
- **Hooks** are shell scripts that execute deterministically — the AI cannot override them. Use hooks for enforcement: run `uv run pytest` after every file edit, block `rm -rf`, require ADR comment before proceeding.

---

## What This Document Drives

The following files must be kept consistent with this workflow. When this doc changes, these must be reviewed:

| File | Construct | What it encodes from this doc |
|---|---|---|
| `.github/copilot-instructions.md` | Workspace instructions | Repo-wide safety rules (file deletion policy, terminal restrictions) |
| `.github/instructions/dev-principles.instructions.md` | File instructions | SOLID, YAGNI, Dependency Rule, shift-left principle |
| `.github/instructions/python.instructions.md` | File instructions | ⚠️ **Does not exist yet** — Python layer rules, Protocol pattern, async, pytest |
| `.github/agents/product-owner.agent.md` | Agent + handoffs | Issue creation workflow, DoR self-validation, handoff to SA |
| `.github/agents/solutions-architect.agent.md` | Agent + handoffs | Interface-first design, ADR triggers, handoff to test-writer |
| `.github/agents/test-writer.agent.md` | Agent + handoffs | Failing tests workflow (pytest/AsyncMock), handoff to implementation |
| `.github/agents/implementation.agent.md` | Agent + handoffs | Pre-implementation checklist, Python stack, handoff to PR review |
| `.github/prompts/write-adr.prompt.md` | Prompt file | `/write-adr` slash command |
| `.github/prompts/refine-user-story.prompt.md` | Prompt file | `/refine-user-story` slash command |
| `.github/prompts/review-architecture.prompt.md` | Prompt file | `/review-architecture` slash command |
| `.github/hooks/adr-reminder.json` | Hook | ADR enforcement at lifecycle events |
| `docs/adr/` | Docs | One ADR per significant decision made during any phase |

**Immediate gaps to address:**
1. Create `.github/instructions/python.instructions.md` — Python layer rules, Protocol, async, pytest (file instructions, `applyTo: **/*.py`)
2. Update `implementation.agent.md` — add `handoffs` frontmatter, replace C#/.NET references with Python stack
3. Update `test-writer.agent.md` — add `handoffs` frontmatter, replace xUnit/FakeItEasy with pytest/AsyncMock
4. Update `solutions-architect.agent.md` — add `handoffs` frontmatter pointing to `test-writer`
5. Update `product-owner.agent.md` — add `handoffs` frontmatter pointing to `solutions-architect`
