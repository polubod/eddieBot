from fastapi import APIRouter, HTTPException
from app.services.web_fetcher import fetch_page_text

router = APIRouter()


@router.get("/fetch")
def fetch_url(url: str):
    try:
        text = fetch_page_text(url)
        return {
            "url": url,
            "text_preview": text[:1000]  # limit output size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
