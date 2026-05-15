# ADR Decision History

This file tracks significant changes to architectural decisions — what changed, from what, to what, and when. Each row corresponds to a revision that would previously have appeared as an inline amendment note in an ADR.

Individual ADRs are written as current-state documents. Refer to this file to understand the evolution of any decision.

---

| Date | ADR | Topic | Change |
|---|---|---|---|
| 2026-05-15 | [ADR-0003](ADR-0003-ai-orchestration.md) | Chat Client | **`FoundryChatClient` (agent-framework)** → **`azure.ai.inference.aio.ChatCompletionsClient`** with `AzureKeyCredential`. Root cause: `FoundryChatClient` internally creates an `AIProjectClient` requiring the `Azure AI Developer` data-plane RBAC role. Executing account holds `Contributor` but cannot self-assign RBAC (`Microsoft.Authorization/roleAssignments/write` required). `ChatCompletionsClient` against the AI Services `/models` endpoint authenticates with API key only. `gpt-4o` (2024-11-20, GlobalStandard) deployed to the AIServices resource via `az cognitiveservices account deployment create` — Contributor access is sufficient. `FoundryChatClient` documented as production path pending RBAC assignment. |
| 2026-05-15 | [ADR-0004](ADR-0004-vector-store.md) | Embedding Client + Model | **`FoundryEmbeddingClient`** → **`azure.ai.inference.aio.EmbeddingsClient`** with `AzureKeyCredential`; **`text-embedding-3-small`** → **`cohere-embed-v3-english`** (serverless MaaS, no separate deployment required). Three runtime fixes: (1) `input_type="text"` is required by the Cohere model on this endpoint — omitting it causes `400 Bad Request`; `"search_document"` / `"search_query"` are rejected. (2) `historical_data.json` uses a `request` field (not `subject`/`description`) — `RagService.load_historical_cases()` now reads `request` first, falling back for forward-compatibility. (3) Auth uses `AzureKeyCredential` (API key) consistent with ADR-0003 changes; `DefaultAzureCredential` fallback retained for Managed Identity in production. |
| 2026-05-13 | [ADR-0003](ADR-0003-ai-orchestration.md) | AI Provider + Foundry Mandate | **Direct OpenAI API** (`OpenAIChatClient(api_key=...)`) → **Azure AI Foundry** (`FoundryChatClient(project_endpoint=..., credential=DefaultAzureCredential())`). Hackathon Coordinators mandated use of Azure AI Foundry and Foundry Agents. All inference now routes through the Foundry project endpoint. `FoundryAgent` documented as the production path for deploying named agents. `openai` package removed as direct dependency; `azure-ai-projects` and `azure-identity` are now transitive deps via `agent-framework[foundry]`. |
| 2026-05-13 | [ADR-0004](ADR-0004-vector-store.md) | RAG Embedding Client | **`AsyncOpenAI`** (direct OpenAI API) → **`FoundryEmbeddingClient`** (Azure AI Foundry inference endpoint). Follows from Foundry mandate in ADR-0003: all AI calls route through Foundry. Requires `FOUNDRY_MODELS_ENDPOINT` in `.env`. Core decision — in-memory for PoC, Azure AI Search for production — unchanged. |
| 2026-05-12 | [ADR-0004](ADR-0004-vector-store.md) | RAG Embedding Client | **`AsyncAzureOpenAI`** (Azure endpoint) → **`AsyncOpenAI`** (direct OpenAI API). Follows from OpenAI provider switch: team uses direct `OPENAI_API_KEY`; Azure OpenAI is the production upgrade path. |
| 2026-05-12 | [ADR-0003](ADR-0003-ai-orchestration.md) | AI Orchestration | **Semantic Kernel 1.34** (`semantic-kernel[azure]`) → **Microsoft Agent Framework 1.3.0** (`agent-framework`). Agent Framework is the official SK successor announced at Build 2025. Migration completed before the PoC ran. See [Migration Detail](#sk--agent-framework-migration-detail) below. |
| 2026-05-12 | [ADR-0004](ADR-0004-vector-store.md) | RAG Storage & Embeddings | **SK `InMemoryVectorStore`** (preview connector) → **`list[list[float]]` + pure-Python cosine similarity**. Follows directly from ADR-0003 migration; SK vector store connector removed. Embeddings now generated via `AsyncOpenAI` (direct OpenAI API). Core decision — in-memory for PoC, Azure AI Search for production — unchanged. |

---

## SK → Agent Framework Migration Detail

Migration completed 2026-05-12. All changes were confined to the Infrastructure layer — `ITriageAgent` and `IRagService` interfaces were untouched. `TriageService` (Application) required only a constructor signature change.

| Concern | Before (Semantic Kernel) | After (Agent Framework) |
|---|---|---|
| Chat client | `AzureChatCompletion` + `Kernel` | `OpenAIChatClient(api_key=...)` |
| Agent creation | `ChatCompletionAgent(kernel=kernel, ...)` | `client.as_agent(name=..., instructions=...)` |
| Classification call | `await kernel.invoke(plugin["classify"], ...)` | `await agent.run(user_message)` |
| Token usage | `KernelFunction` metadata | `response.usage.total_tokens` |
| Embeddings | `AzureTextEmbedding` service on Kernel | `AsyncOpenAI.embeddings.create(...)` |
| Vector store | `InMemoryVectorStore` (SK preview) | `list[list[float]]` + pure-Python cosine similarity |
| Dependency | `semantic-kernel[azure]==1.34.0` | `agent-framework>=1.3.0` + `openai>=1.75.0` |

The `classify_system.txt` prompt and all domain/application layer code were unchanged. Total migration: 6 files, < 2 hours.
