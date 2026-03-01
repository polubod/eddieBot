"""API tests for GET /fetch."""
from unittest.mock import patch, MagicMock
from starlette.testclient import TestClient


@patch("app.api.fetch.fetch_page_text")
def test_fetch_success(mock_fetch: MagicMock, client: TestClient) -> None:
    mock_fetch.return_value = "Page content here " * 100
    response = client.get("/fetch", params={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://example.com"
    assert "text_preview" in data
    assert "Page content here" in data["text_preview"]


@patch("app.api.fetch.fetch_page_text")
def test_fetch_preview_limited_to_1000(mock_fetch: MagicMock, client: TestClient) -> None:
    mock_fetch.return_value = "x" * 2000
    response = client.get("/fetch", params={"url": "https://long.com"})
    assert response.status_code == 200
    assert len(response.json()["text_preview"]) == 1000


def test_fetch_missing_url_returns_422(client: TestClient) -> None:
    response = client.get("/fetch")
    assert response.status_code == 422


@patch("app.api.fetch.fetch_page_text")
def test_fetch_error_returns_500(mock_fetch: MagicMock, client: TestClient) -> None:
    mock_fetch.side_effect = Exception("Connection failed")
    response = client.get("/fetch", params={"url": "https://bad.com"})
    assert response.status_code == 500
    assert "detail" in response.json()
