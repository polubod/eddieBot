import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re
import hashlib
import json
import os
import time

CACHE_DIR = "cache/pages"
CACHE_TTL_SECONDS = 60 * 60 * 6  # 6 hours



def fetch_static_page(url: str) -> str:
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return clean_text(text)

def fetch_dynamic_page(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle")

        # ---- STEP 1: Auto-click "Load More" buttons ----
        for _ in range(10):  # safety cap
            try:
                load_more = page.locator(
                    "button:has-text('Load'), button:has-text('More'), button:has-text('Show')"
                )

                if load_more.count() == 0:
                    break

                load_more.first.click()
                page.wait_for_timeout(1500)

            except Exception:
                break

        # ---- STEP 2: Auto-scroll to bottom ----
        previous_height = None

        for _ in range(10):  # safety cap
            current_height = page.evaluate("document.body.scrollHeight")

            if previous_height == current_height:
                break

            previous_height = current_height
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)

        content = page.content()
        browser.close()

    soup = BeautifulSoup(content, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return clean_text(text)


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"©.*", "", text)
    return text.strip()

def fetch_page_text(url: str) -> str:
    # 1️ Try cache first
    cached = load_from_cache(url)
    if cached:
        print(f"[CACHE HIT] {url}")
        return cached

    print(f"[FETCHING] {url}")

    try:
        text = fetch_static_page(url)

        if len(text) < 500:
            raise ValueError("Likely JS-rendered page")

    except Exception:
        text = fetch_dynamic_page(url)

    # 2️ Save result to cache
    save_to_cache(url, text)

    return text


# Caching utilities
def _cache_path_for_url(url: str) -> str:
    hashed = hashlib.sha256(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{hashed}.json")

def load_from_cache(url: str) -> str | None:
    path = _cache_path_for_url(url)

    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        cached = json.load(f)

    if time.time() - cached["timestamp"] > CACHE_TTL_SECONDS:
        return None

    return cached["content"]

def save_to_cache(url: str, content: str):
    os.makedirs(CACHE_DIR, exist_ok=True)

    path = _cache_path_for_url(url)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": time.time(),
                "content": content
            },
            f,
            ensure_ascii=False
        )

