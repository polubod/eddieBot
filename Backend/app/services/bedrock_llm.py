import re
import boto3
from botocore.exceptions import ClientError

# Pick one:
MODEL_ID = "arn:aws:bedrock:us-west-2:323441263732:inference-profile/us.amazon.nova-pro-v1:0" #amazon.nova-pro-v1:0" 

bedrock = boto3.client("bedrock-runtime", region_name="us-west-2")

SYSTEM_POLICY = """
You are EddieBot, an official SIUE assistant.

Rules:
- Be professional, helpful, and student-friendly.
- Do not be insulting or negative about SIUE or any individuals.
- Avoid controversial topics (politics, hate, explicit content). Redirect back to campus resources.
- Use the provided SIUE webpage information when available.
- If you do not know, say so and suggest where to check (official SIUE site) or ask a clarifying question.
- Do not invent facts, dates, or policies.
- NEVER invent, guess, or rephrase URLs. Only use URLs that are explicitly provided to you.
"""

def format_history(history: list[dict], max_chars: int = 2500) -> str:
    lines = []
    for m in history[-12:]:
        role = "USER" if m["role"] == "user" else "ASSISTANT"
        lines.append(f"{role}: {m['text']}")
    text = "\n".join(lines)
    return text[-max_chars:]


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 100) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start = max(0, end - overlap)
    return chunks


def _converse(prompt: str, max_tokens: int) -> str:
    """
    Unified call for Nova via Bedrock Converse API.
    """
    try:
        resp = bedrock.converse(
            modelId=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ],
            inferenceConfig={
                "maxTokens": max_tokens,
                "temperature": 0.2,
                "topP": 0.9,
            },
        )

        # Bedrock Converse returns an output message with content blocks.
        return resp["output"]["message"]["content"][0]["text"].strip()

    except ClientError as e:
        # Log the real error for debugging (prints in Uvicorn console)
        print("[BEDROCK ERROR]", e)
        raise


def answer_from_chunk(question: str, chunk: str, history_block: str) -> str:
    prompt = f"""

{SYSTEM_POLICY}

CONVERSATION CONTEXT (most recent):
{history_block}

TASK:
- Consider the conversation context above to understand what the student is really asking (e.g. if they say "tell me more", use the prior messages to understand the topic).
- Extract ONLY what helps answer the student question given that context.
- If the question asks about specific resources, services, hours, locations, or items, extract and LIST them concretely with names and relevant details (e.g., hours, room numbers, contact info).
- For general or conversational questions, summarize in 2–5 sentences.
- Do NOT copy page text or UI/navigation labels.
- If a relevant URL is present in the source material, note it so it can be included in the final answer.

If the information is not present, respond with EXACTLY:
NOT_FOUND

UNIVERSITY INFORMATION:
{chunk}

STUDENT QUESTION:
{question}
"""
    return _converse(prompt, max_tokens=450)


def _build_style_hint(category: str) -> str:
    hints = {
        "advising": """
    STYLE:
    - Provide step-by-step guidance the student can follow.
    - Include relevant links, offices, or contact info if present.
    - If scheduling is mentioned, explain the process clearly.
    """,
        "engineering_news": """
    STYLE:
    - Summarize the most recent updates.
    - If dates are present, include them.
    - Give 2–5 key highlights, not a huge list.
    """,
        "events": """
    STYLE:
    - Mention upcoming events and relevant dates/times if present.
    - Keep it brief and offer to narrow by date range or interest.
    """,
        "clubs": """
    STYLE:
    - Explain how to find/join organizations.
    - Avoid long lists unless the student explicitly asks for a list.
    - If giving examples, keep it to 3–6.
    """,
        "tutoring": """
    STYLE:
    - Mention the specific service or resource that fits the student's need.
    - Include hours or contact info if present in the source material.
    - Be encouraging and supportive in tone.
    """,
        "counseling": """
    STYLE:
    - Be warm, empathetic, and non-judgmental.
    - Clearly state how to access services (phone, walk-in, appointment).
    - Remind the student that seeking help is a sign of strength.
    """,
        "financial_aid": """
    STYLE:
    - Break down options or steps clearly.
    - Include deadlines or important dates if present in the source material.
    - Direct the student to the Financial Aid office for personalized guidance.
    """,
        "career": """
    STYLE:
    - Highlight actionable next steps (e.g., visit Handshake, attend a career fair).
    - Mention specific resources like the Career Development Center.
    - Keep it practical and motivating.
    """,
        "registration": """
    STYLE:
    - Give clear, sequential steps the student can follow.
    - Reference systems by name (CougarNet, Banner) if relevant.
    - Mention add/drop deadlines if present in the source material.
    """,
        "graduation": """
    STYLE:
    - Outline the steps to apply for graduation clearly.
    - Include relevant deadlines if present in the source material.
    - Remind the student to confirm requirements with their academic advisor.
    """,
        "engineering_dept": """
    STYLE:
    - Be specific about which department or program the information applies to.
    - Include faculty contacts or office locations if present in the source material.
    - Keep technical details accurate and clear.
    """,
        "library": """
    STYLE:
    - When listing resources or services, use a bullet list with concise descriptions of each item.
    - Always include hours or location details if present in the source material.
    - End with a direct link to the most relevant library page.
    """,
    }
    return hints.get(category, "")


#def generate_answer(question: str, context: str) -> str:
#def generate_answer(question: str, context: str, category: str, history: list[dict]) -> str:
def generate_answer(question: str, context: str, category: str, history: list[dict], allowed_urls: list[str]) -> str:
    chunks = chunk_text(context)

    history_block = format_history(history)
    allowed_links_block = ""
    if allowed_urls:
        allowed_links_block = "ALLOWED LINKS (you may only use these exact URLs):\n" + "\n".join(allowed_urls[:8])

    style_hint = _build_style_hint(category)

    partial_answers: list[str] = []
    for chunk in chunks[:5]:  # cost/time safety cap
        ans = answer_from_chunk(question, chunk, history_block)

        # IMPORTANT: your old check looked for "not found" which misses "NOT_FOUND"
        if ans.strip().upper() != "NOT_FOUND":
            partial_answers.append(ans)

    # if not partial_answers:
    #     return "I couldn't find specific information on SIUE pages to answer that question."

    synthesis_prompt = f"""

{SYSTEM_POLICY} 

Respond in a natural, conversational tone for students.

{style_hint}

CONVERSATION CONTEXT (most recent):
{history_block}

{allowed_links_block}
LINK RULES:
- Only include links from ALLOWED LINKS above.
- Never invent, guess, rewrite, or “pretty print” URLs.
- If no ALLOWED LINKS are relevant, do not include any links.

Combine the partial answers into ONE clear answer.
- Remove duplicates
- If the student asked about specific resources, services, hours, or items, present them as a formatted bullet list with relevant details.
- For general or conversational questions, use plain prose (2–4 sentences).
- Do NOT invent new information
- Answer the student directly. Do not quote webpage text
- Always end with a relevant URL from ALLOWED LINKS if one is available.

PARTIAL ANSWERS:
{chr(10).join(partial_answers)}
"""
    return _converse(synthesis_prompt, max_tokens=500)


def generate_answer_stream(question: str, context: str, category: str, history: list[dict], allowed_urls: list[str]):
    """
    Same as generate_answer but streams the synthesis step token-by-token.
    Chunk extraction runs normally first, then the synthesis is streamed.
    Yields str tokens.
    """
    chunks = chunk_text(context)
    history_block = format_history(history)

    allowed_links_block = ""
    if allowed_urls:
        allowed_links_block = "ALLOWED LINKS (you may only use these exact URLs):\n" + "\n".join(allowed_urls[:8])

    style_hint = _build_style_hint(category)

    partial_answers: list[str] = []
    for chunk in chunks[:5]:
        ans = answer_from_chunk(question, chunk, history_block)
        if ans.strip().upper() != "NOT_FOUND":
            partial_answers.append(ans)

    synthesis_prompt = f"""

{SYSTEM_POLICY} 

Respond in a natural, conversational tone for students.

{style_hint}

CONVERSATION CONTEXT (most recent):
{history_block}

{allowed_links_block}
LINK RULES:
- Only include links from ALLOWED LINKS above.
- Never invent, guess, rewrite, or "pretty print" URLs.
- If no ALLOWED LINKS are relevant, do not include any links.

Combine the partial answers into ONE clear answer.
- Remove duplicates
- If the student asked about specific resources, services, hours, or items, present them as a formatted bullet list with relevant details.
- For general or conversational questions, use plain prose (2–4 sentences).
- Do NOT invent new information
- Answer the student directly. Do not quote webpage text
- Always end with a relevant URL from ALLOWED LINKS if one is available.

PARTIAL ANSWERS:
{chr(10).join(partial_answers)}
"""
    try:
        resp = bedrock.converse_stream(
            modelId=MODEL_ID,
            messages=[{"role": "user", "content": [{"text": synthesis_prompt}]}],
            inferenceConfig={"maxTokens": 400, "temperature": 0.2, "topP": 0.9},
        )
        for event in resp["stream"]:
            if "contentBlockDelta" in event:
                token = event["contentBlockDelta"]["delta"].get("text", "")
                if token:
                    yield token
    except ClientError as e:
        print("[BEDROCK STREAM ERROR]", e)
        raise
