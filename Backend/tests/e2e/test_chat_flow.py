"""End-to-end tests: full chat flow through the API."""
import pytest
from unittest.mock import patch
from starlette.testclient import TestClient


@pytest.fixture
def mock_external_services():
    """Mock Bedrock and retrieval for E2E so tests don't call AWS or external URLs."""
    with patch("app.api.chat.retrieve_context", return_value="SIUE is a university in Edwardsville."):
        with patch("app.api.chat.generate_answer", return_value="SIUE is a great university."):
            yield


def test_e2e_chat_full_flow(client: TestClient, mock_external_services) -> None:
    """E2E: POST /chat with classification, memory, and response."""
    session_id = "e2e-session-1"
    r1 = client.post(
        "/chat",
        json={"session_id": session_id, "message": "What is SIUE?"},
    )
    assert r1.status_code == 200
    data1 = r1.json()
    assert data1["reply"] == "SIUE is a great university."
    assert data1["category"] in ("general", "engineering_news", "advising", "events", "clubs", "tutoring", "counseling")

    r2 = client.post(
        "/chat",
        json={"session_id": session_id, "message": "Tell me about advising"},
    )
    assert r2.status_code == 200
    data2 = r2.json()
    assert "reply" in data2
    assert data2["category"] == "advising"


def test_e2e_chat_blocked_then_allowed(client: TestClient, mock_external_services) -> None:
    """E2E: blocked message returns canned reply; next allowed message works."""
    session_id = "e2e-session-2"
    r_blocked = client.post(
        "/chat",
        json={"session_id": session_id, "message": "something about vote"},
    )
    assert r_blocked.status_code == 200
    assert r_blocked.json()["category"] == "blocked"

    r_ok = client.post(
        "/chat",
        json={"session_id": session_id, "message": "What events are there?"},
    )
    assert r_ok.status_code == 200
    assert r_ok.json()["category"] == "events"


def test_e2e_chat_no_context_fallback(client: TestClient) -> None:
    """E2E: when retrieval returns empty, endpoint still returns a reply (via generate_answer)."""
    with patch("app.api.chat.retrieve_context", return_value=""):
        with patch("app.api.chat.generate_answer", return_value="No SIUE pages found for that."):
            r = client.post(
                "/chat",
                json={"session_id": "e2e-session-3", "message": "obscure question xyz"},
            )
    assert r.status_code == 200
    assert r.json()["reply"] == "No SIUE pages found for that."
