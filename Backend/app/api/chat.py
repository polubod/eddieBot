from fastapi import APIRouter
from pydantic import BaseModel

from app.services.query_classifier import classify_query
from app.services.retrieval import retrieve_context
from app.services.memory_singleton import memory_store
from app.services.bedrock_llm import generate_answer
from app.services.safety_guard import check_request
from app.services.sources import UNIVERSITY_SOURCES

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    category: str


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    # Get session ID once, early
    session_id = getattr(request, "session_id", None) or "dev-session"

    allowed, blocked_reply = check_request(request.message)
    if not allowed:
        memory_store.add(session_id, "user", request.message)
        memory_store.add(session_id, "assistant", blocked_reply)
        return ChatResponse(reply=blocked_reply, category="blocked")

    # Store the user's message FIRST so history includes it
    memory_store.add(session_id, "user", request.message)

    category = classify_query(request.message)
    context = retrieve_context(category, request.message)

    # Now history contains the latest user message
    history = memory_store.get(session_id)

    if not context:
        reply = (
            "I couldn't find specific university information for that question yet. "
            "Try asking about events, clubs, or advising."
        )
    else:
        try:
            allowed_urls = UNIVERSITY_SOURCES.get(category, [])
            reply = generate_answer(
                question=request.message,
                context=context,
                category=category,
                history=history,
                allowed_urls = UNIVERSITY_SOURCES.get(category, [])
            )
        except Exception as e:
            print("[BEDROCK ERROR]", e)
            reply = (
                "AI is temporarily unavailable while the model configuration is being finalized. "
                "Please try again shortly."
            )

    # Store assistant reply after generating it
    memory_store.add(session_id, "assistant", reply)

    return ChatResponse(reply=reply, category=category)
