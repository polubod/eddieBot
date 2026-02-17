def classify_query(message: str) -> str:
    m = message.lower()

    if any(k in m for k in ["engineering news", "soe news", "siue engineering", "school of engineering update"]):
        return "engineering_news"

    if any(k in m for k in ["advising", "advisor", "academic advising", "starfish", "meet with my advisor"]):
        return "advising"

    if any(k in m for k in ["event", "calendar", "competition", "workshop", "seminar"]):
        return "events"

    if any(k in m for k in ["club", "organization", "student org", "get involved", "join"]):
        return "clubs"

    # DEFAULT
    return "general"


