from __future__ import annotations
from dataclasses import dataclass
from typing import Deque, Dict, List
from collections import deque
import time

@dataclass
class Message:
    role: str   # "user" or "assistant"
    text: str
    ts: float

class SessionMemoryStore:
    """
    Per-session history in RAM with TTL.
    Good for dev / single-server hosting.
    Later: swap to Redis/DynamoDB with same interface.
    """
    def __init__(self, max_messages: int = 12, ttl_seconds: int = 60 * 60):
        self.max_messages = max_messages
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, Deque[Message]] = {}
        self._last_seen: Dict[str, float] = {}

    def _cleanup(self) -> None:
        now = time.time()
        expired = [sid for sid, t in self._last_seen.items() if now - t > self.ttl_seconds]
        for sid in expired:
            self._store.pop(sid, None)
            self._last_seen.pop(sid, None)

    def get(self, session_id: str) -> List[dict]:
        self._cleanup()
        self._last_seen[session_id] = time.time()
        history = self._store.get(session_id, deque())
        return [{"role": m.role, "text": m.text} for m in history]

    def add(self, session_id: str, role: str, text: str) -> None:
        self._cleanup()
        self._last_seen[session_id] = time.time()
        if session_id not in self._store:
            self._store[session_id] = deque(maxlen=self.max_messages)
        self._store[session_id].append(Message(role=role, text=text, ts=time.time()))
