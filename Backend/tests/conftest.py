"""
Shared pytest fixtures for EddieBot Backend tests.
Provides TestClient, memory store reset, and common mocks.
"""
import pytest
from unittest.mock import patch, MagicMock
from starlette.testclient import TestClient

from app.main import app
from app.services.memory_singleton import memory_store


@pytest.fixture
def client():
    """FastAPI/Starlette TestClient for API and E2E tests."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_memory_store():
    """Reset in-memory store between tests to avoid cross-test leakage.
    Uses internal state; if SessionMemoryStore gains a clear() API, prefer that."""
    yield
    memory_store._store.clear()
    memory_store._last_seen.clear()


@pytest.fixture
def mock_bedrock():
    """Patch generate_answer to avoid real AWS calls."""
    with patch("app.api.chat.generate_answer") as m:
        m.return_value = "This is a test reply from the assistant."
        yield m


@pytest.fixture
def mock_retrieve_context():
    """Patch retrieve_context to return controlled context."""
    with patch("app.api.chat.retrieve_context") as m:
        m.return_value = "Sample SIUE context for testing."
        yield m


@pytest.fixture
def mock_fetch_page_text():
    """Patch fetch_page_text for retrieval and web_fetcher tests."""
    with patch("app.services.web_fetcher.fetch_page_text") as m:
        m.return_value = "Sample page content for tests."
        yield m
