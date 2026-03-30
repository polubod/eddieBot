import pytest
from src.app import create_app
from tests.fakes import FakeLLM

def test_chat_success():
    fake_llm = FakeLLM(reply="(fake) hello")
    app = create_app(fake_llm)
    app.testing = True
    client = app.test_client()

    response = client.post("/api/chat", json={"message": "Hi"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["reply"] == "(fake) hello"
    assert fake_llm.calls == ["Hi"]

def test_chat_empty_message_returns_400():
    fake_llm = FakeLLM()
    app = create_app(fake_llm)
    app.testing = True
    client = app.test_client()

    response = client.post("/api/chat", json={"message": "   "})
    assert response.status_code == 400

def test_chat_llm_failure_returns_502():
    fake_llm = FakeLLM(fail=True)
    app = create_app(fake_llm)
    app.testing = True
    client = app.test_client()

    response = client.post("/api/chat", json={"message": "Hi"})
    assert response.status_code == 502