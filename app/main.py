from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.routers.transliteration import router as transliteration

app = FastAPI(
    title="MyTransliterator",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transliteration)

