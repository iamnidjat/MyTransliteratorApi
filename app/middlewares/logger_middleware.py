import logging
import time
from fastapi import Request
from starlette.types import ASGIApp, Receive, Scope, Send
from logging.handlers import RotatingFileHandler
import os

# --- Logger setup ---
logger = logging.getLogger("api_logger")
logger.setLevel(logging.INFO)

# /app/logs (two levels up from middlewares folder)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to logs folder inside the same folder as this script
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

# ensures the logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# INFO handler
info_handler = RotatingFileHandler(os.path.join(LOG_DIR, "info.log"), maxBytes=5_000_000, backupCount=5, encoding="utf-8")
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# ERROR handler
error_handler = RotatingFileHandler(os.path.join(LOG_DIR, "error.log"), maxBytes=5_000_000, backupCount=5, encoding="utf-8")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

if not logger.handlers:
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)


class LoggingMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app  # saves the FastAPI/ASGI app instance

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # only handles HTTP requests; pass through other types (like websockets)
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        path = scope.get("path", "")
        if path in {"/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"}:
            await self.app(scope, receive, send)
            return

        # # --- reads the body manually and replays for the app ---
        # body = b""  # to store full request body
        # more_body = True
        # messages = []

        # while more_body:
        #     message = await receive()  # reads original ASGI request
        #     messages.append(message)
        #     if message["type"] == "http.request":
        #         body += message.get("body", b"")
        #         more_body = message.get("more_body", False)

        # Re-inject messages so the app can read the body normally
        # async def receive_wrapper():
        #     return messages.pop(0) if messages else {"type": "http.request", "body": b"", "more_body": False}

        # request = Request(scope, receive=receive_wrapper)  # wraps ASGI scope into a FastAPI Request
        request = Request(scope, receive=receive) 
        start_time = time.time()  # records start time for duration logging
        # body_text = body.decode("utf-8") if body else None  # decodes to string

        # response_body = []  # stores response body chunks here
        status_code = None # to capture response status code

        # wrapper to intercept response messages
        async def send_wrapper(message):
            # if message["type"] == "http.response.body":  # only captures body messages
            #     response_body.append(message.get("body", b""))  # saves response bytes
            # await send(message)  # passes message to the real send function
            nonlocal status_code

            if message["type"] == "http.response.start":  # only captures status code
                status_code = message["status"] # saves status code

            await send(message) # passes data to the real send function
        
        client = scope.get("client")
        ip = client[0] if client else "unknown"

        try:
            # calls the actual app with our send wrapper
            # await self.app(scope, receive=receive_wrapper, send=send_wrapper)
            await self.app(scope, receive=receive, send=send_wrapper)

            duration = time.time() - start_time  # calculates request duration
          ##  response_text = b"".join(response_body).decode("utf-8") if response_body else ""  # decodes response

            status_code = status_code or 500
            # INFO log: method, URL, duration, request and response bodies
            logger.info(
                 f"{request.method} {request.url} "
                 f"status={status_code} duration={duration:.3f}s ip={ip}"
            )
        except Exception as exc:
            # ERROR log: log exception with stack trace and request info
            duration = time.time() - start_time
            status_code = status_code or 500
            logger.exception(
                f"Unhandled exception -> {request.method} {request.url} "
                f"status={status_code} duration={duration:.3f}s ip={ip}"
            )
            raise  # Re-raise exception to let FastAPI handle it