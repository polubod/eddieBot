from app.services.session_memory import SessionMemoryStore

memory_store = SessionMemoryStore(
    max_messages=12,
    ttl_seconds=60 * 60
)
