from fastapi import FastAPI
from app.api.routers.transliteration import router as transliteration

app = FastAPI(
    title="MyTransliterator",
    version="0.1.0",
)

app.include_router(transliteration)

