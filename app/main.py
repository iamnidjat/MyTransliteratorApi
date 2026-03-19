from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from app.api.routers.v1.transliteration import router as transliteration
from app.api.routers.v1.auth import router as auth
from app.exceptions.handlers import AppException
from fastapi.responses import JSONResponse
from app.middlewares.logger_middleware import LoggingMiddleware
from app.utils.custom_response_codes import MESSAGES, ResponseCode

app = FastAPI(
    title="MyTransliterator",
    version="0.1.0",
)

app.add_middleware(LoggingMiddleware)
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
    message = MESSAGES.get(exc.business_code, "Unknown error")

    return JSONResponse(
        status_code=exc.http_status,
        content={
            "code": exc.business_code,
            "message": message,
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "business_code": ResponseCode.SERVER_ERROR,
            "message": MESSAGES[ResponseCode.SERVER_ERROR],
            "data": str(exc)  # actual error message
        },
    )


