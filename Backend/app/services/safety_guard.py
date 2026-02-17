def check_request(message: str) -> tuple[bool, str]:
    """
    Returns (allowed, response_if_blocked).
    Keep this simple and deterministic.
    """
    m = message.lower()

    blocked_keywords = [
        # politics / elections / lobbying
        "vote", "election", "democrat", "republican", "trump", "biden", "politics",
        # hate/harassment
        "hate", "racist", "slur",
        # violence / self-harm
        "kill", "suicide", "self harm", "bomb", "weapon", "gun",
        # explicit sexual content
        "porn", "sex",
    ]

    if any(k in m for k in blocked_keywords):
        return (False,
                "I can’t help with that topic. If you have questions about SIUE programs, campus services, "
                "events, clubs, advising, or university resources, I can help.")

    return (True, "")
