import pytest
from unittest.mock import MagicMock

from triage_assistant.infrastructure.rag_service import RagService


@pytest.fixture
def settings():
    s = MagicMock()
    s.foundry_models_endpoint = None
    s.foundry_project_endpoint = "https://example.services.ai.azure.com/api/projects/proj"
    s.embedding_deployment = "text-embedding-3-small"
    s.historical_data_path = "data/help_requests/historical_data.json"
    return s


@pytest.fixture
def rag(settings):
    return RagService(settings)


async def test_search_returns_list(rag):
    results = await rag.search("duplicate records on work order 55")
    assert isinstance(results, list)
