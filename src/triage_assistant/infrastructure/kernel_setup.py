"""Microsoft Agent Framework client factory — builds a FoundryChatClient
routed through Azure AI Foundry. Consumed by triage_agent.py.
"""

from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

from triage_assistant.config import TriageSettings


def build_chat_client(settings: TriageSettings) -> FoundryChatClient:
    """Return a configured FoundryChatClient routed through Azure AI Foundry.

    Uses DefaultAzureCredential — supports az login locally and Managed Identity in CI.
    Docs: https://learn.microsoft.com/en-us/agent-framework/agents/providers/
    """
    return FoundryChatClient(
        project_endpoint=settings.foundry_project_endpoint,
        model=settings.chat_deployment,
        credential=DefaultAzureCredential(),
    )
