---
applyTo: "**/*.py"
---

# Python Coding Standards — DCI Triage Assistant

## Layer Import Rules

The Dependency Rule is inviolable. Inner rings never import from outer rings.

| Layer | Location | Allowed imports | Forbidden |
|---|---|---|---|
| Domain | `src/triage_assistant/domain/` | stdlib + `pydantic.BaseModel` | Any third-party AI/HTTP SDK |
| Application | `src/triage_assistant/application/` | Domain + `typing.Protocol` | Infrastructure, FastAPI, OpenAI SDK |
| Infrastructure | `src/triage_assistant/infrastructure/` | Application interfaces + any SDK | Direct domain mutation |
| API | `src/triage_assistant/api/` | Application + FastAPI | Direct infrastructure calls bypassing application |

If you see `openai`, `agent_framework`, `httpx`, or `requests` imported inside `domain/` or `application/`, that is a Dependency Rule violation — stop and fix it before proceeding.

---

## Interfaces — `Protocol`, Never `ABC`

Define all seams in `src/triage_assistant/application/interfaces.py` using `typing.Protocol`. Concrete classes do not import the Protocol — structural subtyping means the match is implicit.

```python
# application/interfaces.py
from typing import Protocol
from triage_assistant.domain.models import HelpRequest, TriageResult

class ITriageAgent(Protocol):
    async def classify(self, request: HelpRequest) -> TriageResult: ...

class IHistoricalCaseRepository(Protocol):
    async def get_similar_cases(self, subject: str, description: str) -> list[TriageResult]: ...
```

Never use `ABC` or `@abstractmethod`. If you see them, replace with `Protocol`.

---

## Async — Always `async/await`

All service methods that call I/O (network, file, AI SDK) must be `async def`. No sync wrappers around async code. Never call `asyncio.run()` inside a service method.

```python
# Good
async def classify(self, request: HelpRequest) -> TriageResult:
    response = await self._agent.run(user_message)
    return self._parse(response.text)

# Bad — sync wrapper around async
def classify_sync(self, request: HelpRequest) -> TriageResult:
    return asyncio.run(self.classify(request))  # Never do this in a service
```

---

## Type Hints — Mandatory on All Public Signatures

Every `def` and `async def` that is not a private helper (`_name`) must have complete type annotations on parameters and return type. Use `from __future__ import annotations` at the top of files to enable forward references.

```python
# Good
async def classify(self, request: HelpRequest) -> TriageResult: ...

# Bad
async def classify(self, request): ...
```

---

## Data Models — `pydantic.BaseModel` in Domain, `BaseSettings` for Config

Domain DTOs use `pydantic.BaseModel`. Configuration uses `pydantic_settings.BaseSettings` — never read `os.environ` directly inside service classes.

```python
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Domain DTO
class HelpRequest(BaseModel):
    request_id: str
    subject: str
    description: str
    account_id: str

# Config — reads from .env at startup
class TriageSettings(BaseSettings):
    openai_api_key: SecretStr
    chat_deployment: str = "gpt-4o"
    confidence_threshold: float = 0.85
    model_config = SettingsConfigDict(env_file=".env")
```

Validate config at startup in the FastAPI lifespan event — fail fast, not at request time.

---

## MAF Agent Pattern

One concern per agent. An agent that classifies does not also suggest resolutions. If the `instructions` string exceeds ~300 words, it has more than one concern — split it.

```python
from agent_framework.foundry import FoundryChatClient
from agent_framework import Agent, AgentResponse
from azure.identity import DefaultAzureCredential

client = FoundryChatClient(
    project_endpoint=settings.foundry_project_endpoint,
    model=settings.chat_deployment,
    credential=DefaultAzureCredential(),
)
agent = client.as_agent(name="triage-classifier", instructions=system_prompt)

# Use response_format for structured output — forces raw JSON, no ```json fences
response: AgentResponse[TriageResult] = await agent.run(
    user_message,
    options={"response_format": TriageResult},
)
result: TriageResult = response.value

# Production: swap to FoundryAgent for a named agent deployed in Foundry
# from agent_framework.foundry import FoundryAgent
# agent = FoundryAgent(
#     project_endpoint=settings.foundry_project_endpoint,
#     agent_name=settings.foundry_agent_name,
#     credential=DefaultAzureCredential(),
# )
```

---

## FastAPI Conventions

Register routes in router modules — never inline in `main.py`:

```python
# api/routes/triage.py
from fastapi import APIRouter, Depends
from triage_assistant.application.interfaces import ITriageAgent
from triage_assistant.domain.models import HelpRequest, TriageResult

router = APIRouter(prefix="/api", tags=["triage"])

@router.post("/triage", response_model=TriageResult)
async def triage(request: HelpRequest, agent: ITriageAgent = Depends(get_triage_agent)) -> TriageResult:
    return await agent.classify(request)
```

Use FastAPI's `lifespan` for startup validation — fail fast if required config is missing.

---

## Testing — `pytest` + `pytest-asyncio`

Test file names mirror the source tree: `tests/test_application/test_triage_service.py` for `src/triage_assistant/application/triage_service.py`.

Function naming: `test_<method>_<state_under_test>_<expected_behaviour>`

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_classify_low_confidence_returns_needs_human_review():
    mock_agent = AsyncMock(spec=ITriageAgent)
    mock_agent.classify.return_value = TriageResult(
        classification="Needs Human Review",
        confidence=0.72,
        rationale="Vague description.",
        follow_up_question="Which system is affected?",
        resolution=None,
    )
    service = TriageService(agent=mock_agent)
    result = await service.process(low_detail_request)
    assert result.classification == "Needs Human Review"
    assert result.follow_up_question is not None
```

- Mock against `Protocol` interfaces only — never against concrete classes or third-party SDKs
- Tests must be deterministic: no `datetime.now()`, no real network calls, no random data
- Run tests with `uv run pytest`
- Failing tests in TDD must be marked `@pytest.mark.xfail(strict=True, reason="implementation not yet written")`

---

## Package Management

```bash
uv sync              # install all deps from pyproject.toml
uv add <package>     # add a runtime dependency
uv add --dev <pkg>   # add a dev/test-only dependency
uv run pytest        # run tests inside the venv
uv run uvicorn triage_assistant.api.main:app --reload
```

Never use `pip install` in this project. All dependency changes must go through `pyproject.toml` via `uv add`.

---

## Security

- **Never commit secrets.** Use `.env` (gitignored) locally; environment variables in CI.
- **Always use `SecretStr`** for API keys in `BaseSettings`. Access the value only with `.get_secret_value()` at the point of use — do not store the unwrapped string.
- **Parse AI responses strictly** with `pydantic` `model_validate_json()` — never `eval()`, never `exec()`, never `json.loads()` into a plain dict that is then trusted without validation.
- **Validate all inputs at the API boundary.** FastAPI request models (pydantic `BaseModel`) handle this automatically — do not re-validate deep in the call stack.
