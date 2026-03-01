from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from app.api.routers.v1.transliteration import router as transliteration
from app.api.routers.v1.auth import router as auth
from app.exceptions.handlers import AppException
from fastapi.responses import JSONResponse
from app.utils.custom_response_codes import MESSAGES

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

app.include_router(auth)
app.include_router(transliteration)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "code": exc.code,
            "message": MESSAGES[exc.code],
        },
    )



