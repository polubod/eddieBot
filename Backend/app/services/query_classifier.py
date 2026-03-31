def classify_query(message: str) -> str:
    m = message.lower()

    if any(k in m for k in [
        "counseling", "counselling", "counselor", "therapy", "mental health",
        "anxiety", "stress", "depression", "wellness", "crisis", "caps"
    ]):
        return "counseling"

    if any(k in m for k in [
        "financial aid", "fafsa", "scholarship", "grant", "loan", "tuition",
        "afford", "billing", "bursar", "stipend", "fellowship",
        "cost of attendance", "financial assistance", "aid package"
    ]):
        return "financial_aid"

    if any(k in m for k in [
        "career", "internship", "co-op", "coop", "resume", "cover letter",
        "interview", "job fair", "career fair", "handshake", "career center",
        "employer", "recruit", "hiring", "job search", "full-time job", "part-time job"
    ]):
        return "career"

    if any(k in m for k in [
        "register", "registration", "enroll", "enrollment", "add a class",
        "drop a class", "withdraw", "waitlist", "class schedule",
        "cougarnet", "banner", "credit hour", "section", "crn"
    ]):
        return "registration"

    if any(k in m for k in [
        "graduate", "graduation", "commencement", "apply to graduate",
        "degree requirement", "capstone", "degree audit", "degree plan",
        "senior audit"
    ]):
        return "graduation"

    if any(k in m for k in [
        "advising", "advisor", "academic advisor", "starfish", "meet with my advisor"
    ]):
        return "advising"

    if any(k in m for k in [
        "tutoring", "tutor", "study help", "academic help", "help with math", "si",
        "writing center", "writing lab", "learning support", "supplemental instruction",
        "si sessions", "office hours", "peer mentor", "homework help"
    ]):
        return "tutoring"

    if any(k in m for k in [
        "library", "lovejoy", "study room", "study space", "study spot", "study area",
        "book", "journal", "database", "reserve a room", "makerlab", "librarian",
        "research appointment", "borrow", "interlibrary", "print", "printing"
    ]):
        return "library"

    if any(k in m for k in [
        "engineering news", "soe news", "siue engineering news", "school of engineering update"
    ]):
        return "engineering_news"

    if any(k in m for k in [
        "event", "calendar", "competition", "workshop", "seminar", "conference", "hackathon"
    ]):
        return "events"

    if any(k in m for k in [
        "club", "organization", "student org", "get involved", "join a club",
        "ieee", "acm", "nsbe", "swe", "asme"
    ]):
        return "clubs"

    if any(k in m for k in [
        "electrical engineering", "computer engineering", "mechanical engineering",
        "civil engineering", "industrial engineering", "engineering department",
        "ece department", "construction management", "professor", "faculty",
        "research lab", "engineering program", "engineering curriculum"
    ]):
        return "engineering_dept"

    # DEFAULT
    return "general"


