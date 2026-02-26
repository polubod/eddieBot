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
- Extract ONLY what helps answer the student question.
- Summarize in 2–5 sentences.
- If answering with a list would make sense, such as a list of clubs or events, you may add that after the summary.
- Do NOT copy page text or UI/navigation labels.

If the information is not present, respond with EXACTLY:
NOT_FOUND

UNIVERSITY INFORMATION:
{chunk}

STUDENT QUESTION:
{question}
"""
    return _converse(prompt, max_tokens=200)


#def generate_answer(question: str, context: str) -> str:
#def generate_answer(question: str, context: str, category: str, history: list[dict]) -> str:
def generate_answer(question: str, context: str, category: str, history: list[dict], allowed_urls: list[str]) -> str:
    chunks = chunk_text(context)

    history_block = format_history(history)
    allowed_links_block = ""
    if allowed_urls:
        allowed_links_block = "ALLOWED LINKS (you may only use these exact URLs):\n" + "\n".join(allowed_urls[:8])

    style_hint = ""
    if category == "advising":
        style_hint = """
    STYLE:
    - Provide step-by-step guidance the student can follow.
    - Include relevant links, offices, or contact info if present.
    - If scheduling is mentioned, explain the process clearly.
    """

    elif category == "engineering_news":
        style_hint = """
    STYLE:
    - Summarize the most recent updates.
    - If dates are present, include them.
    - Give 2–5 key highlights, not a huge list.
    """

    elif category == "events":
        style_hint = """
    STYLE:
    - Mention upcoming events and relevant dates/times if present.
    - Keep it brief and offer to narrow by date range or interest.
    """

    elif category == "clubs":
        style_hint = """
    STYLE:
    - Explain how to find/join organizations.
    - Avoid long lists unless the student explicitly asks for a list.
    - If giving examples, keep it to 3–6.
    """

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
- Avoid long lists unless the student asked for a list
- Do NOT invent new information
- Answer the student directly. Do not quote webpage text

PARTIAL ANSWERS:
{chr(10).join(partial_answers)}
"""
    return _converse(synthesis_prompt, max_tokens=400)
