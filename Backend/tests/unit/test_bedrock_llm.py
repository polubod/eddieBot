"""Unit tests for app.services.bedrock_llm."""
import pytest
from unittest.mock import patch, MagicMock
from app.services.bedrock_llm import (
    format_history,
    chunk_text,
    answer_from_chunk,
    generate_answer,
)


def test_format_history_empty() -> None:
    assert format_history([]) == ""


def test_format_history_single() -> None:
    out = format_history([{"role": "user", "text": "Hi"}])
    assert "USER" in out
    assert "Hi" in out


def test_format_history_assistant() -> None:
    out = format_history([{"role": "assistant", "text": "Hello there"}])
    assert "ASSISTANT" in out
    assert "Hello there" in out


def test_format_history_truncates_by_max_chars() -> None:
    long = [{"role": "user", "text": "x" * 3000}]
    out = format_history(long, max_chars=500)
    assert len(out) <= 500 + 50


def test_format_history_keeps_last_twelve() -> None:
    many = [{"role": "user", "text": f"msg{i}"} for i in range(20)]
    out = format_history(many, max_chars=5000)
    assert "msg19" in out
    assert "msg0" not in out


def test_chunk_text_empty() -> None:
    assert chunk_text("") == []


def test_chunk_text_small() -> None:
    text = "one two three"
    chunks = chunk_text(text, chunk_size=5, overlap=1)
    assert len(chunks) >= 1
    assert "one" in chunks[0]


def test_chunk_text_overlap() -> None:
    words = ["w" + str(i) for i in range(100)]
    text = " ".join(words)
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    assert len(chunks) >= 2
    for c in chunks:
        assert len(c.split()) <= 25


@patch("app.services.bedrock_llm._converse")
def test_answer_from_chunk_returns_converse_result(mock_converse: MagicMock) -> None:
    mock_converse.return_value = "The answer is X."
    result = answer_from_chunk("Q?", "context", "history")
    assert result == "The answer is X."
    mock_converse.assert_called_once()


@patch("app.services.bedrock_llm._converse")
def test_generate_answer_returns_synthesis(mock_converse: MagicMock) -> None:
    # One chunk -> one answer_from_chunk call, then one synthesis call
    mock_converse.side_effect = ["Partial A", "Final combined answer"]
    result = generate_answer(
        question="What is SIUE?",
        context="SIUE is a university.",
        category="general",
        history=[],
        allowed_urls=[],
    )
    assert result == "Final combined answer"


@patch("app.services.bedrock_llm._converse")
def test_generate_answer_all_not_found_returns_synthesis(mock_converse: MagicMock) -> None:
    """When all chunk answers are NOT_FOUND, synthesis is still called and its result returned."""
    mock_converse.side_effect = ["NOT_FOUND", "No relevant SIUE information found."]
    result = generate_answer(
        question="?",
        context="some context",
        category="general",
        history=[],
        allowed_urls=[],
    )
    assert result == "No relevant SIUE information found."


@patch("app.services.bedrock_llm._converse")
def test_generate_answer_mixed_not_found_uses_partial(mock_converse: MagicMock) -> None:
    mock_converse.side_effect = ["NOT_FOUND", "Found something.", "Synthesis here"]
    result = generate_answer(
        question="?",
        context="a " * 2000,
        category="general",
        history=[],
        allowed_urls=[],
    )
    assert "Synthesis here" in result or "Found something" in result


@pytest.mark.parametrize("category", ["advising", "engineering_news", "events", "clubs", "tutoring", "counseling"])
@patch("app.services.bedrock_llm._converse")
def test_generate_answer_style_hints_per_category(mock_converse: MagicMock, category: str) -> None:
    mock_converse.side_effect = ["Partial answer", "Synthesis"]
    result = generate_answer(
        question="Q?",
        context="Context here.",
        category=category,
        history=[],
        allowed_urls=[],
    )
    assert result == "Synthesis"


@patch("app.services.bedrock_llm.bedrock")
def test_converse_success(mock_bedrock: MagicMock) -> None:
    from app.services.bedrock_llm import _converse
    mock_bedrock.converse.return_value = {
        "output": {"message": {"content": [{"text": "  Model reply  "}]}}
    }
    result = _converse("prompt", max_tokens=100)
    assert result == "Model reply"
    mock_bedrock.converse.assert_called_once()


@patch("app.services.bedrock_llm.bedrock")
def test_converse_client_error_raises(mock_bedrock: MagicMock) -> None:
    from botocore.exceptions import ClientError
    from app.services.bedrock_llm import _converse
    mock_bedrock.converse.side_effect = ClientError({"Error": {"Code": "500", "Message": "Error"}}, "converse")
    with pytest.raises(ClientError):
        _converse("prompt", max_tokens=100)
