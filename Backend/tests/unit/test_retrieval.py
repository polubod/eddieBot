"""Unit tests for app.services.retrieval."""
from unittest.mock import patch, MagicMock
from app.services.retrieval import select_sources, retrieve_context


def test_select_sources_engineering_news() -> None:
    urls = select_sources("engineering_news", "anything")
    assert isinstance(urls, list)
    assert len(urls) >= 1
    assert any("siue.edu" in u for u in urls)


def test_select_sources_advising() -> None:
    urls = select_sources("advising", "advising")
    assert len(urls) >= 1


def test_select_sources_events() -> None:
    urls = select_sources("events", "events")
    assert len(urls) >= 1


def test_select_sources_clubs() -> None:
    urls = select_sources("clubs", "clubs")
    assert len(urls) >= 1


def test_select_sources_general_with_keywords() -> None:
    urls = select_sources("general", "housing and dorm")
    assert len(urls) >= 1
    assert any("housing" in u for u in urls)

    urls = select_sources("general", "dining and meal plan")
    assert len(urls) >= 1

    urls = select_sources("general", "admission apply")
    assert len(urls) >= 1

    urls = select_sources("general", "major program degree")
    assert len(urls) >= 1

    urls = select_sources("general", "engineering")
    assert len(urls) >= 1

    urls = select_sources("general", "recreation gym fitness")
    assert len(urls) >= 1


def test_select_sources_general_fallback() -> None:
    urls = select_sources("general", "something random")
    assert len(urls) == 2
    assert "siue.edu" in urls[0] and "siue.edu" in urls[1]


def test_select_sources_general_cap_three() -> None:
    urls = select_sources("general", "housing dining admission")
    assert len(urls) <= 3


@patch("app.services.retrieval.fetch_page_text")
def test_retrieve_context_success(mock_fetch: MagicMock) -> None:
    mock_fetch.return_value = "Page content here"
    result = retrieve_context("general", "hello")
    assert "Page content here" in result
    assert mock_fetch.called


@patch("app.services.retrieval.fetch_page_text")
def test_retrieve_context_fetch_error_continues(mock_fetch: MagicMock) -> None:
    mock_fetch.side_effect = [Exception("fail"), "Second page ok"]
    result = retrieve_context("events", "events")
    assert "Second page ok" in result


@patch("app.services.retrieval.fetch_page_text")
def test_retrieve_context_all_fail_returns_empty(mock_fetch: MagicMock) -> None:
    mock_fetch.side_effect = Exception("fail")
    result = retrieve_context("general", "hello")
    assert result == ""
