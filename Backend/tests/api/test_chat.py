"""API tests for POST /chat."""
from unittest.mock import patch
from starlette.testclient import TestClient


def test_chat_success(client: TestClient, mock_bedrock, mock_retrieve_context) -> None:
    response = client.post(
        "/chat",
        json={"session_id": "test-session-1", "message": "What events are there?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert data["reply"] == "This is a test reply from the assistant."
    assert data["category"] == "events"


def test_chat_no_context_calls_generate_answer(client: TestClient, mock_bedrock) -> None:
    """When retrieval returns no context, endpoint still calls generate_answer with placeholder context."""
    with patch("app.api.chat.retrieve_context", return_value=""):
        response = client.post(
            "/chat",
            json={"session_id": "test-session-2", "message": "xyz random"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "This is a test reply from the assistant."


def test_chat_bedrock_error_returns_graceful_message(client: TestClient, mock_retrieve_context) -> None:
    with patch("app.api.chat.generate_answer", side_effect=Exception("AWS error")):
        response = client.post(
            "/chat",
            json={"session_id": "test-session-3", "message": "Tell me about advising"},
        )
    assert response.status_code == 200
    data = response.json()
    assert "AI is temporarily unavailable" in data["reply"] or "unavailable" in data["reply"].lower()


def test_chat_blocked_content_returns_blocked_reply(client: TestClient) -> None:
    response = client.post(
        "/chat",
        json={"session_id": "test-session-4", "message": "tell me about vote and election"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "blocked"
    assert "help" in data["reply"].lower() and "SIUE" in data["reply"]


def test_chat_requires_session_id_returns_422(client: TestClient) -> None:
    """Request body without session_id is rejected by Pydantic."""
    response = client.post("/chat", json={"message": "events?"})
    assert response.status_code == 422


def test_chat_invalid_body_returns_422(client: TestClient) -> None:
    response = client.post("/chat", json={})
    assert response.status_code == 422


def test_chat_memory_persists_in_session(client: TestClient, mock_bedrock, mock_retrieve_context) -> None:
    sid = "memory-session-1"
    client.post("/chat", json={"session_id": sid, "message": "First message"})
    response = client.post("/chat", json={"session_id": sid, "message": "Second message"})
    assert response.status_code == 200
    mock_bedrock.assert_called()
    call_kwargs = mock_bedrock.call_args
    history = call_kwargs[1]["history"]
    assert any(m["text"] == "First message" for m in history)
    assert len(history) >= 2
