# ADR-0003: AI Orchestration — Microsoft Agent Framework + Azure AI Foundry

**Status:** Accepted  
**Date:** 2026-05-12 (revised 2026-05-13)  
**Team:** Team Captain America

---

## Context

The triage assistant needs to call an LLM for chat completion (classification). The team must decide whether to use Microsoft's AI orchestration framework as a structured agent layer, or call the `openai` Python SDK directly.

DCI has a preference for Microsoft technologies and the Hackathon Coordinators have mandated use of **Azure AI Foundry** and **Foundry Agents** for AI service hosting. **Microsoft Agent Framework** (`agent-framework`) is Microsoft's recommended Python AI orchestration framework — the official successor to both Semantic Kernel and AutoGen, announced at Microsoft Build 2025. Its `foundry` provider connects natively to Azure AI Foundry projects.

---

## Decision

Use **Microsoft Agent Framework** (`agent-framework>=1.3.0`) with the **`FoundryChatClient` provider** for inference and **`FoundryAgent`** for connecting to agents deployed in Azure AI Foundry.

---

## Considered Options

| Option | Brief Description |
|---|---|
| A — MAF `FoundryChatClient` + `Agent` | `FoundryChatClient(project_endpoint=..., model=..., credential=...)` → `client.as_agent(instructions=...)` → `agent.run()`; agent logic defined in code |
| B — MAF `FoundryAgent` | Connects to a PromptAgent or HostedAgent **already deployed** in Azure AI Foundry by name; no local `instructions` needed |
| C — MAF `OpenAIChatClient` (direct API) | `OpenAIChatClient(api_key=...)` — no Foundry, no Azure; original PoC path |
| D — Direct `azure-ai-projects` SDK | `AIProjectClient.inference.get_azure_openai_client()` — bypasses MAF orchestration layer |
| E — LangChain | Non-Microsoft framework |

---

## Rationale

- **Chose Option A for the classification agent:** `FoundryChatClient` routes all inference through the Foundry project endpoint — satisfying the mandate while keeping agent instructions co-located with code. No separate Foundry agent deployment step required; the agent is defined in `infrastructure/agents/triage_agent.py` and the Foundry endpoint is swappable via config.

- **Option B (`FoundryAgent`) is the production pattern:** When the team publishes the triage classifier as a named PromptAgent in Foundry (e.g. `"dci-triage-classifier"`), the infrastructure implementation switches to `FoundryAgent(project_endpoint=..., agent_name="dci-triage-classifier", ...)` with no Application layer changes. The `ITriageAgent` seam absorbs the swap.

- **Rejected Option C (direct API):** Contradicts the Foundry mandate from Hackathon Coordinators. Left documented as the fallback if Foundry is unavailable.

- **Rejected Option D (raw SDK):** Bypasses MAF middleware (retry, telemetry, compaction) — value that would need reimplementation manually.

- **Rejected Option E (LangChain):** Non-Microsoft; conflicts with DCI's technology preference.

---

## Implementation

### Option A — Code-defined agent via `FoundryChatClient` (current)

```python
# infrastructure/agents/triage_agent.py
from agent_framework.foundry import FoundryChatClient
from agent_framework import Agent, AgentResponse
from azure.identity import DefaultAzureCredential

client = FoundryChatClient(
    project_endpoint=settings.foundry_project_endpoint,
    model=settings.chat_deployment,
    credential=DefaultAzureCredential(),
)
agent: Agent = client.as_agent(
    name="dci-triage-classifier",
    instructions=system_prompt,
)
response: AgentResponse[TriageResult] = await agent.run(
    user_message,
    options={"response_format": TriageResult},
)
result: TriageResult = response.value
```

### Option B — Foundry-deployed agent (production upgrade)

```python
# infrastructure/agents/triage_agent.py
from agent_framework.foundry import FoundryAgent
from azure.identity import DefaultAzureCredential

agent = FoundryAgent(
    project_endpoint=settings.foundry_project_endpoint,
    agent_name=settings.foundry_agent_name,
    agent_version=settings.foundry_agent_version,
    credential=DefaultAzureCredential(),
)
response: AgentResponse = await agent.run(user_message)
result = TriageResult.model_validate_json(response.text)
```

---

## Consequences

- ✅ Satisfies Hackathon Coordinator mandate: all inference routes through Azure AI Foundry
- ✅ `ITriageAgent` seam is preserved — swap from Option A → B is Infrastructure-only
- ✅ `DefaultAzureCredential` supports local dev (Azure CLI login) and CI (Managed Identity) without code changes
- ✅ `agent-framework` telemetry integrates with Azure Monitor via `FoundryChatClient.configure_azure_monitor()`
- ⚠️ Requires `FOUNDRY_PROJECT_ENDPOINT` in `.env` — fails fast at startup if missing
- ⚠️ `agent-framework` requires `[tool.uv] prerelease = "allow"` in `pyproject.toml`
- ⚠️ `azure-ai-projects` and `azure-identity` are now transitive dependencies (pulled in by `agent-framework[foundry]`)
- ❌ Option C (direct `OPENAI_API_KEY`) no longer the default; available as a fallback by swapping to `OpenAIChatClient`

---

## References

- [Microsoft Agent Framework — Overview](https://learn.microsoft.com/en-us/agent-framework/)
- [agent-framework on PyPI](https://pypi.org/project/agent-framework/)
- [Azure AI Foundry — Overview](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [azure-identity DefaultAzureCredential](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential)
- [ADR-0005: Agent Framework Migration Detail](ADR-0005-agent-framework-migration.md)
