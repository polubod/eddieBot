"""Unit tests for app.services.sources (data and structure)."""
from app.services.sources import UNIVERSITY_SOURCES


def test_university_sources_has_expected_categories() -> None:
    expected = {"clubs", "events", "advising", "engineering_news", "general", "tutoring", "counseling"}
    assert set(UNIVERSITY_SOURCES.keys()) == expected


def test_all_sources_are_siue_urls() -> None:
    for category, urls in UNIVERSITY_SOURCES.items():
        assert isinstance(urls, list)
        for url in urls:
            assert url.startswith("https://")
            assert "siue.edu" in url
