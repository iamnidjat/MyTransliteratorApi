import secrets
import os
from datetime import datetime, timedelta, timezone
import uuid
from fastapi import HTTPException, status
from jose import ExpiredSignatureError, jwt, JWTError
from dotenv import load_dotenv
from app.auth.jwt_based_blacklist import is_token_blacklisted

load_dotenv()

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7))

def create_access_token(data: dict):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "iat": now, # issued at
        "type": "access",
        "jti": str(uuid.uuid4())
    })
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def create_refresh_token():
    return secrets.token_urlsafe(64)

def decode_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
def verify_token(token: str):
    payload = decode_token(token)

    jti = payload.get("jti")

    if not jti:
        raise HTTPException(
            status_code=401,
            detail="Invalid token structure"
        )

    if is_token_blacklisted(jti):
        raise HTTPException(
            status_code=401,
            detail="Token has been revoked (logout or banned)"
        )

    return payload