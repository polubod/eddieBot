from app.services.sources import UNIVERSITY_SOURCES
from app.services.web_fetcher import fetch_page_text

def select_sources(category: str, message: str) -> list[str]:
    urls = UNIVERSITY_SOURCES.get(category, [])

    if category != "general":
        return urls

    m = message.lower()

    keyword_map = [
        (["housing", "dorm", "residence"], "https://www.siue.edu/housing/"),
        (["dining", "meal plan", "food"], "https://www.siue.edu/dining/"),
        (["admission", "apply"], "https://www.siue.edu/admissions/"),
        (["major", "program", "degree", "academics"], "https://www.siue.edu/academics/"),
        (["engineering"], "https://www.siue.edu/engineering/"),
        (["recreation", "gym", "fitness"], "https://www.siue.edu/campus-recreation/"),
    ]

    picked = []
    for keys, url in keyword_map:
        if any(k in m for k in keys):
            picked.append(url)

    if not picked:
        picked = ["https://www.siue.edu/", "https://www.siue.edu/about/"]

    return picked[:3]  # cap for speed/quality

def retrieve_context(category: str, message: str) -> str:
    urls = select_sources(category, message)

    texts = []
    for url in urls:
        try:
            texts.append(fetch_page_text(url))
        except Exception as e:
            print("[FETCH ERROR]", url, e)

    return "\n\n".join(texts)
