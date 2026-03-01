"""API tests for root and app wiring."""
from starlette.testclient import TestClient

from app.main import app


def test_root_returns_status(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "EddieBot backend is running"


def test_app_includes_chat_router() -> None:
    routes = [r.path for r in app.routes]
    assert "/chat" in routes or any("/chat" in getattr(r, "path", "") for r in app.routes)


def test_app_includes_fetch_router() -> None:
    routes = [r.path for r in app.routes]
    assert any("fetch" in getattr(r, "path", "") for r in app.routes)
