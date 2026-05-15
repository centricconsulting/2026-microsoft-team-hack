"""Application configuration — all settings read from environment variables or .env.

TriageSettings is constructed once in main.py lifespan and passed to every
infrastructure component. No other module should import from os.environ directly.
All required fields raise a validation error at startup if missing, so
misconfiguration fails fast before any requests are served.
"""
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class TriageSettings(BaseSettings):
    """Pydantic-settings model that reads configuration from .env or environment variables.

    Field names are the canonical env var names in SCREAMING_SNAKE_CASE
    (pydantic-settings converts automatically, e.g. foundry_project_endpoint
    reads from FOUNDRY_PROJECT_ENDPOINT).
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Azure AI Foundry — required; startup fails immediately if these are missing
    foundry_project_endpoint: str   # Full project URL, e.g. https://<resource>.services.ai.azure.com/api/projects/<proj>
    foundry_api_key: str | None = None  # Cognitive Services API key; if set, skips DefaultAzureCredential for model calls
    helpdesk_api_key: SecretStr     # Reserved for future helpdesk auth; currently unused by the open API

    # Azure AI Foundry — optional, sensible defaults for the hackathon environment
    chat_deployment: str = "gpt-4o"                        # Model used by TriageAgent for classification
    embedding_deployment: str = "text-embedding-3-small"   # Model used by RagService for vector embeddings
    foundry_models_endpoint: str | None = None             # Override inference endpoint; derived from project endpoint if unset
    foundry_agent_name: str | None = None                  # Named Foundry agent (Option B in ADR-0003); unused in current PoC
    foundry_agent_version: str | None = None               # Version of the named Foundry agent; unused in current PoC

    # DCI Helpdesk
    helpdesk_base_url: str = "https://app-x2slazjwhcxuq.azurewebsites.net"  # Shared external service; same URL in dev and prod

    # Triage behaviour
    confidence_threshold: float = 0.85               # Classifications below this score are escalated to Needs Human Review
    historical_data_path: str = "data/help_requests/historical_data.json"  # RAG source data loaded at startup
    routing_rules_path: str = "data/routing_rules.md"                      # Routing rules injected into the agent system prompt
