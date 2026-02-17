from fastapi import APIRouter
from pydantic import BaseModel

from app.services.query_classifier import classify_query
from app.services.retrieval import retrieve_context
from app.services.memory_singleton import memory_store
from app.services.bedrock_llm import generate_answer
from app.services.safety_guard import check_request


router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    category: str


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    # Get session ID early
    session_id = getattr(request, "session_id", None) or "dev-session"

    allowed, blocked_reply = check_request(request.message)
    if not allowed:
        # still store history so the conversation feels consistent
        memory_store.add(session_id, "user", request.message)
        memory_store.add(session_id, "assistant", blocked_reply)
        return ChatResponse(reply=blocked_reply, category="blocked")

    
    category = classify_query(request.message)
    context = retrieve_context(category, request.message)

    session_id = request.session_id
    history = memory_store.get(session_id)

    if not context:
        reply = (
            "I couldn't find specific university information for that question yet. "
            "Try asking about events, clubs, or advising."
        )
    else:
        try:
            reply = (
                generate_answer(question=request.message, context=context, category=category, history=history)
                # f"Based on current SIUE information related to {category}:\n\n"
                # f"{context[:1500]}"
            )
        except Exception as e:
            print("[BEDROCK ERROR]", e)
            reply = "AI is temporarily unavailable while the model configuration is being finalized. Please try again shortly."

    memory_store.add(session_id, "user", request.message)
    memory_store.add(session_id, "assistant", reply)

    return ChatResponse(
        reply=reply,
        category=category
    )
