"""Unit tests for app.services.safety_guard."""
import pytest
from app.services.safety_guard import check_request


@pytest.mark.parametrize(
    "message",
    [
        "vote for president",
        "election day",
        "democrat",
        "republican",
        "trump",
        "biden",
        "politics",
        "hate speech",
        "racist",
        "slur",
        "kill",
        "suicide",
        "self harm",
        "bomb",
        "weapon",
        "gun",
        "porn",
        "sex",
    ],
)
def test_check_request_blocked(message: str) -> None:
    allowed, reply = check_request(message)
    assert allowed is False
    assert "help" in reply.lower() and ("can" in reply.lower() or "SIUE" in reply)
    assert "SIUE" in reply or "programs" in reply


def test_check_request_allowed() -> None:
    allowed, reply = check_request("What events are there?")
    assert allowed is True
    assert reply == ""

    allowed, reply = check_request("Tell me about advising.")
    assert allowed is True
    assert reply == ""


def test_check_request_case_insensitive() -> None:
    allowed, _ = check_request("VOTE")
    assert allowed is False
    allowed, _ = check_request("Vote")
    assert allowed is False
