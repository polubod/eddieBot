"""End-to-end tests: fetch flow through the API."""
from unittest.mock import patch, MagicMock
from starlette.testclient import TestClient


@patch("app.api.fetch.fetch_page_text")
def test_e2e_fetch_returns_preview(mock_fetch: MagicMock, client: TestClient) -> None:
    """E2E: GET /fetch returns url and text_preview."""
    mock_fetch.return_value = "Full page content. " * 200
    response = client.get("/fetch", params={"url": "https://www.siue.edu/"})
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://www.siue.edu/"
    assert len(data["text_preview"]) <= 1000
    assert "Full page content" in data["text_preview"]


@patch("app.api.fetch.fetch_page_text")
def test_e2e_fetch_error_propagates(mock_fetch: MagicMock, client: TestClient) -> None:
    """E2E: GET /fetch on failure returns 500 with detail."""
    mock_fetch.side_effect = RuntimeError("Network error")
    response = client.get("/fetch", params={"url": "https://invalid.example.com"})
    assert response.status_code == 500
    assert "detail" in response.json()
