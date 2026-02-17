from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.fetch import router as fetch_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="EddieBot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(fetch_router)

@app.get("/")
def root():
    return {"status": "EddieBot backend is running"}
