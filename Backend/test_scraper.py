from app.services.web_fetcher import fetch_page_text

url = "https://getinvolved.siue.edu/organizations"
text = fetch_page_text(url)

print(text[:5500])
