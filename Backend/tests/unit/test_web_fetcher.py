"""Unit tests for app.services.web_fetcher."""
import hashlib
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from app.services.web_fetcher import (
    clean_text,
    fetch_static_page,
    fetch_page_text,
    _cache_path_for_url,
    load_from_cache,
    save_to_cache,
)


def test_clean_text() -> None:
    assert clean_text("  a   b  \n c  ") == "a b c"
    assert clean_text("x © 2024 SIUE") == "x"
    assert clean_text("") == ""


@patch("app.services.web_fetcher.requests.get")
def test_fetch_static_page_success(mock_get: MagicMock) -> None:
    mock_resp = MagicMock()
    mock_resp.text = "<html><body><p>Hello</p></body></html>"
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    result = fetch_static_page("https://example.com")
    assert "Hello" in result
    mock_get.assert_called_once_with("https://example.com", timeout=10)


@patch("app.services.web_fetcher.requests.get")
def test_fetch_static_page_decomposes_script_style(mock_get: MagicMock) -> None:
    mock_resp = MagicMock()
    mock_resp.text = "<html><body><script>x=1</script><style>.x{}</style><p>Body</p></body></html>"
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    result = fetch_static_page("https://example.com")
    assert "Body" in result
    assert "x=1" not in result
    assert ".x" not in result


@patch("app.services.web_fetcher.clean_text")
@patch("app.services.web_fetcher.sync_playwright")
def test_fetch_dynamic_page_success(mock_playwright: MagicMock, mock_clean: MagicMock) -> None:
    mock_clean.return_value = "Cleaned dynamic content"
    mock_browser = MagicMock()
    mock_page = MagicMock()
    mock_page.content.return_value = "<html><body><p>Dynamic</p></body></html>"
    mock_browser.new_page.return_value = mock_page
    mock_p = MagicMock()
    mock_p.chromium.launch.return_value = mock_browser
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_p
    mock_cm.__exit__.return_value = None
    mock_playwright.return_value = mock_cm

    from app.services.web_fetcher import fetch_dynamic_page
    result = fetch_dynamic_page("https://example.com")
    assert result == "Cleaned dynamic content"
    mock_page.goto.assert_called_once()
    mock_browser.close.assert_called_once()


def test_cache_path_for_url() -> None:
    path = _cache_path_for_url("https://example.com/page")
    assert "cache" in path
    assert path.endswith(".json")
    assert _cache_path_for_url("https://a.com") != _cache_path_for_url("https://b.com")


def test_save_and_load_from_cache(tmp_path: Path) -> None:
    with patch("app.services.web_fetcher.CACHE_DIR", str(tmp_path)):
        save_to_cache("https://test.com", "Cached content")
        loaded = load_from_cache("https://test.com")
        assert loaded == "Cached content"


def test_load_from_cache_missing_returns_none() -> None:
    assert load_from_cache("https://nonexistent-cache-url-12345.com") is None


def test_load_from_cache_expired_returns_none(tmp_path: Path) -> None:
    with patch("app.services.web_fetcher.CACHE_DIR", str(tmp_path)):
        save_to_cache("https://expired.com", "Old")
    key = hashlib.sha256(b"https://expired.com").hexdigest()
    path = Path(tmp_path) / f"{key}.json"
    with open(path) as f:
        data = json.load(f)
    data["timestamp"] = time.time() - 60 * 60 * 24
    with open(path, "w") as f:
        json.dump(data, f)
    with patch("app.services.web_fetcher.CACHE_DIR", str(tmp_path)):
        assert load_from_cache("https://expired.com") is None


@patch("app.services.web_fetcher.load_from_cache")
@patch("app.services.web_fetcher.fetch_static_page")
@patch("app.services.web_fetcher.save_to_cache")
def test_fetch_page_text_cache_hit(
    mock_save: MagicMock,
    mock_static: MagicMock,
    mock_load: MagicMock,
) -> None:
    mock_load.return_value = "From cache"
    result = fetch_page_text("https://cached.com")
    assert result == "From cache"
    mock_static.assert_not_called()
    mock_save.assert_not_called()


@patch("app.services.web_fetcher.load_from_cache")
@patch("app.services.web_fetcher.fetch_static_page")
@patch("app.services.web_fetcher.save_to_cache")
def test_fetch_page_text_static_success(
    mock_save: MagicMock,
    mock_static: MagicMock,
    mock_load: MagicMock,
) -> None:
    mock_load.return_value = None
    mock_static.return_value = "Static content " * 100
    result = fetch_page_text("https://static.com")
    assert "Static content" in result
    mock_save.assert_called_once()


@patch("app.services.web_fetcher.load_from_cache")
@patch("app.services.web_fetcher.fetch_static_page")
@patch("app.services.web_fetcher.fetch_dynamic_page")
@patch("app.services.web_fetcher.save_to_cache")
def test_fetch_page_text_falls_back_to_dynamic(
    mock_save: MagicMock,
    mock_dynamic: MagicMock,
    mock_static: MagicMock,
    mock_load: MagicMock,
) -> None:
    mock_load.return_value = None
    mock_static.side_effect = ValueError("Likely JS-rendered")
    mock_dynamic.return_value = "Dynamic content " * 100
    result = fetch_page_text("https://spa.com")
    assert "Dynamic content" in result
    mock_dynamic.assert_called_once_with("https://spa.com")
