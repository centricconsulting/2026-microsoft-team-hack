# ADR-0003: AI Orchestration — Azure AI Inference SDK + Azure AI Foundry

**Status:** Accepted  
**Date:** 2026-05-12 (revised 2026-05-13, 2026-05-15)  
**Team:** Team Captain America

---

## Context

The triage assistant needs to call an LLM for chat completion (classification). The team must decide whether to use Microsoft's AI orchestration framework as a structured agent layer, or call the `openai` Python SDK directly.

DCI has a preference for Microsoft technologies and the Hackathon Coordinators have mandated use of **Azure AI Foundry** and **Foundry Agents** for AI service hosting. **Microsoft Agent Framework** (`agent-framework`) is Microsoft's recommended Python AI orchestration framework — the official successor to both Semantic Kernel and AutoGen, announced at Microsoft Build 2025. Its `foundry` provider connects natively to Azure AI Foundry projects.

During hackathon execution (2026-05-15) it was discovered that `FoundryChatClient` internally creates an `AIProjectClient` (`azure-ai-projects`) which requires the **Azure AI Developer** data-plane RBAC role on the Foundry resource. The executing account holds `Contributor` at subscription scope but lacks `Microsoft.Authorization/roleAssignments/write` — the role cannot be self-assigned. `azure.ai.inference.aio.ChatCompletionsClient` provides the same chat completion capability via the AI Services multi-model inference endpoint (`/models/chat/completions`) and authenticates with an API key — no data-plane RBAC required.

---

## Decision

Use **`azure.ai.inference.aio.ChatCompletionsClient`** (`azure-ai-inference`) with **`AzureKeyCredential`** against the Azure AI Services multi-model inference endpoint (`https://<resource>.services.ai.azure.com/models`). The model (`gpt-4o`) is deployed as a standard deployment on the `AIServices` resource via `az cognitiveservices account deployment create`.

`FoundryChatClient` remains the documented production path for when an `Azure AI Developer` role is assigned — the `ITriageAgent` seam means the swap is Infrastructure-only.

---

## Considered Options

| Option | Brief Description |
|---|---|
| A — MAF `FoundryChatClient` + `Agent` | `FoundryChatClient(project_endpoint=..., model=..., credential=...)` → `client.as_agent(instructions=...)` → `agent.run()`; agent logic defined in code |
| B — MAF `FoundryAgent` | Connects to a PromptAgent or HostedAgent **already deployed** in Azure AI Foundry by name; no local `instructions` needed |
| C — MAF `OpenAIChatClient` (direct API) | `OpenAIChatClient(api_key=...)` — no Foundry, no Azure; original PoC path |
| D — Direct `azure-ai-projects` SDK | `AIProjectClient.inference.get_azure_openai_client()` — bypasses MAF orchestration layer |
| E — LangChain | Non-Microsoft framework |
| F — `azure-ai-inference` `ChatCompletionsClient` | `ChatCompletionsClient(endpoint=.../models, credential=AzureKeyCredential(...))` → `client.complete(messages)`; no RBAC required; same SDK used for embeddings |

---

## Rationale

- **Chose Option F (`azure-ai-inference ChatCompletionsClient`) as the current implementation:** `FoundryChatClient` (Option A) requires the `Azure AI Developer` data-plane RBAC role on the Foundry resource. The hackathon account holds `Contributor` but cannot self-assign RBAC roles (`Microsoft.Authorization/roleAssignments/write` is required). `ChatCompletionsClient` authenticates via API key against the AI Services `/models` inference endpoint — the same endpoint and SDK already used for embeddings (ADR-0004). A `gpt-4o` (2024-11-20, GlobalStandard) deployment was created on the resource via `az cognitiveservices account deployment create` — Contributor access is sufficient for this operation.

- **Option A (`FoundryChatClient`) is the production path:** Once the `Azure AI Developer` role is granted, revert `triage_agent.py` to use `FoundryChatClient` with `DefaultAzureCredential`. The `ITriageAgent` seam means this is an Infrastructure-only change.

- **Option B (`FoundryAgent`) remains the long-term production pattern:** When the triage classifier is published as a named PromptAgent in Foundry, the infrastructure implementation switches with no Application layer changes.

- **Rejected Option C (direct API):** Contradicts the Foundry mandate from Hackathon Coordinators.

- **Rejected Option D (raw SDK):** `AIProjectClient` has the same RBAC requirement as `FoundryChatClient`.

- **Rejected Option E (LangChain):** Non-Microsoft; conflicts with DCI's technology preference.

---

## Implementation

### Option F — `azure-ai-inference ChatCompletionsClient` (current)

```python
# infrastructure/agents/triage_agent.py
from azure.ai.inference.aio import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

# Endpoint: https://<resource>.services.ai.azure.com/models
# API key preferred locally; DefaultAzureCredential for Managed Identity in production
base = settings.foundry_project_endpoint.split("/api/projects")[0]
models_endpoint = f"{base.rstrip('/')}/models"

credential = (
    AzureKeyCredential(settings.foundry_api_key)
    if settings.foundry_api_key
    else DefaultAzureCredential()
)
self._client = ChatCompletionsClient(endpoint=models_endpoint, credential=credential)

# Classification call
response = await self._client.complete(
    messages=[
        SystemMessage(content=system_prompt),
        UserMessage(content=user_message),
    ],
    model=settings.chat_deployment,  # "gpt-4o"
)
raw = response.choices[0].message.content
data = json.loads(raw)
```

### Option A — `FoundryChatClient` (production path, requires Azure AI Developer role)

```python
# infrastructure/agents/triage_agent.py
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

client = FoundryChatClient(
    project_endpoint=settings.foundry_project_endpoint,
    model=settings.chat_deployment,
    credential=DefaultAzureCredential(),
)
agent = client.as_agent(name="dci-triage-classifier", instructions=system_prompt)
response = await agent.run(user_message)
result = TriageResult.model_validate_json(response.text)
```

### Option B — Foundry-deployed PromptAgent (long-term production)

```python
from agent_framework.foundry import FoundryAgent
from azure.identity import DefaultAzureCredential

agent = FoundryAgent(
    project_endpoint=settings.foundry_project_endpoint,
    agent_name=settings.foundry_agent_name,
    credential=DefaultAzureCredential(),
)
response = await agent.run(user_message)
result = TriageResult.model_validate_json(response.text)
```

---

## Consequences

- ✅ Satisfies Hackathon Coordinator mandate: inference routes through Azure AI Foundry resource endpoint
- ✅ `ITriageAgent` seam is preserved — swap from Option F → A → B is Infrastructure-only
- ✅ `AzureKeyCredential` works without any RBAC role — API key sufficient for AI Services data plane
- ✅ `DefaultAzureCredential` fallback path retained — Managed Identity works in production once RBAC is assigned
- ✅ No new dependencies — `azure-ai-inference` is already present for embeddings (ADR-0004)
- ⚠️ Requires `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_API_KEY` in `.env` — fails fast at startup if missing
- ⚠️ `agent-framework` telemetry (`FoundryChatClient.configure_azure_monitor()`) is not available on this path — OpenTelemetry instrumentation must be added manually if needed
- ⚠️ `agent-framework` remains a `pyproject.toml` dependency for the Option A/B upgrade path; requires `[tool.uv] prerelease = "allow"`
- ❌ `FoundryChatClient` (Option A) blocked until `Azure AI Developer` role is assigned to the executing identity on the Foundry resource

---

## References

- [azure-ai-inference Python SDK](https://learn.microsoft.com/en-us/azure/ai-services/reference/sdk-package-reference-python)
- [ChatCompletionsClient — Azure AI Inference](https://learn.microsoft.com/en-us/python/api/azure-ai-inference/azure.ai.inference.chatcompletionsclient)
- [Microsoft Agent Framework — Overview](https://learn.microsoft.com/en-us/agent-framework/)
- [Azure AI Foundry — Overview](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [azure-identity DefaultAzureCredential](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential)
- [az cognitiveservices account deployment create](https://learn.microsoft.com/en-us/cli/azure/cognitiveservices/account/deployment)
- [ADR-0004: Vector Store & Embeddings](ADR-0004-vector-store.md)
