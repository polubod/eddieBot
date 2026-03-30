from src.app import create_app
from tests.fakes import FakeLLM

def test_llm_timeout_returns_504():
    fake_llm = FakeLLM(timeout=True)
    app = create_app(fake_llm)
    app.testing = True
    client = app.test_client()

    response = client.post("/api/chat", json={"message": "Hi"})
    assert response.status_code == 504
    assert "timeout" in response.get_json()["error"].lower()

def test_llm_failure_returns_502():
    llm = FakeLLM(fail=True)
    app = create_app(llm)
    app.testing = True
    client = app.test_client()

    response = client.post("/api/chat", json={"message": "Hi"})
    assert response.status_code == 502