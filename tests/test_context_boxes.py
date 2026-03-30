import pytest
from src.app import create_app
from tests.fakes import FakeLLM

@pytest.mark.xfail(reason="Context boxes not implemented yet")
def test_context_boxes():
    llm = FakeLLM(reply="ok")
    app = create_app(llm)
    app.testing = True
    client = app.test_client()

    response = client.post("/api/chat", json={"message": "Where is tutoring?"})
    assert response.status_code == 200

    sent_input = llm.calls[0]

    assert "freshman" in sent_input.lower()
    assert "campus resources" in sent_input.lower()