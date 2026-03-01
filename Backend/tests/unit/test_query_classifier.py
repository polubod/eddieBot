"""Unit tests for app.services.query_classifier."""
import pytest
from app.services.query_classifier import classify_query


@pytest.mark.parametrize(
    "message,expected",
    [
        ("What is the latest engineering news?", "engineering_news"),
        ("SOE news today", "engineering_news"),
        ("latest engineering news", "engineering_news"),
        ("school of engineering update", "engineering_news"),
        ("I need advising", "advising"),
        ("Who is my advisor?", "advising"),
        ("academic advising", "advising"),
        ("starfish", "advising"),
        ("meet with my advisor", "advising"),
        ("tutoring", "tutoring"),
        ("writing center", "tutoring"),
        ("counseling", "counseling"),
        ("mental health", "counseling"),
        ("Upcoming event", "events"),
        ("calendar", "events"),
        ("competition", "events"),
        ("workshop", "events"),
        ("seminar", "events"),
        ("student club", "clubs"),
        ("organization", "clubs"),
        ("student org", "clubs"),
        ("get involved", "clubs"),
        ("how do I join?", "clubs"),
        ("hello", "general"),
        ("what is SIUE?", "tutoring"),
        ("random question", "general"),
    ],
)
def test_classify_query(message: str, expected: str) -> None:
    assert classify_query(message) == expected


def test_classify_query_case_insensitive() -> None:
    assert classify_query("ENGINEERING NEWS") == "engineering_news"
    assert classify_query("Advising") == "advising"
