"""End-to-end tests: full stack (root + chat + fetch) in one run."""
from unittest.mock import patch
from starlette.testclient import TestClient


@patch("app.api.chat.generate_answer")
@patch("app.api.chat.retrieve_context")
def test_e2e_root_then_chat_then_fetch(
    mock_retrieve: patch,
    mock_generate: patch,
    client: TestClient,
) -> None:
    """E2E: hit root, then chat, then fetch in sequence."""
    mock_retrieve.return_value = "Context"
    mock_generate.return_value = "Reply"

    r_root = client.get("/")
    assert r_root.status_code == 200
    assert "EddieBot" in r_root.json()["status"]

    r_chat = client.post(
        "/chat",
        json={"session_id": "stack-session", "message": "Hello"},
    )
    assert r_chat.status_code == 200
    assert r_chat.json()["reply"] == "Reply"

    with patch("app.api.fetch.fetch_page_text", return_value="Fetched text"):
        r_fetch = client.get("/fetch", params={"url": "https://example.com"})
    assert r_fetch.status_code == 200
    assert "Fetched text" in r_fetch.json()["text_preview"]
