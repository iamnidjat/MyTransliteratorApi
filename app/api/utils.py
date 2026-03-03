import os
from dotenv import load_dotenv
from fastapi import Response

load_dotenv()

REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

def set_auth_cookie(response: Response, token_value: str):
    response.set_cookie(
        key="refresh_token",
        value=token_value,
        httponly=True,
        secure=False, 
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/",
    )
    
    return response