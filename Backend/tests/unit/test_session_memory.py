"""Unit tests for app.services.session_memory (SessionMemoryStore)."""
import time
from unittest.mock import patch
import pytest
from app.services.session_memory import SessionMemoryStore, Message


def test_message_dataclass() -> None:
    m = Message(role="user", text="hi", ts=1.0)
    assert m.role == "user"
    assert m.text == "hi"
    assert m.ts == 1.0


def test_store_add_and_get() -> None:
    store = SessionMemoryStore(max_messages=5, ttl_seconds=3600)
    store.add("s1", "user", "Hello")
    store.add("s1", "assistant", "Hi there")
    history = store.get("s1")
    assert len(history) == 2
    assert history[0] == {"role": "user", "text": "Hello"}
    assert history[1] == {"role": "assistant", "text": "Hi there"}


def test_store_max_messages() -> None:
    store = SessionMemoryStore(max_messages=3, ttl_seconds=3600)
    for i in range(5):
        store.add("s1", "user", f"msg{i}")
    history = store.get("s1")
    assert len(history) == 3
    assert history[0]["text"] == "msg2"
    assert history[-1]["text"] == "msg4"


def test_store_multiple_sessions() -> None:
    store = SessionMemoryStore(max_messages=5, ttl_seconds=3600)
    store.add("s1", "user", "a")
    store.add("s2", "user", "b")
    assert store.get("s1") == [{"role": "user", "text": "a"}]
    assert store.get("s2") == [{"role": "user", "text": "b"}]


def test_store_ttl_cleanup() -> None:
    store = SessionMemoryStore(max_messages=5, ttl_seconds=1)
    store.add("s1", "user", "hi")
    assert len(store.get("s1")) == 1
    with patch("time.time", return_value=time.time() + 7200):
        store._cleanup()
    history = store.get("s1")
    assert len(history) == 0


def test_get_nonexistent_session_returns_empty_list() -> None:
    store = SessionMemoryStore(max_messages=5, ttl_seconds=3600)
    assert store.get("nonexistent") == []
