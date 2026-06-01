from webbrowser import get

from app.core.models.user_model import User
from fastapi import HTTPException, Depends, Request
from app.auth.dependencies import get_current_user, get_optional_current_user
from app.core.redis import redis_client

# for now using sync redis client, will be changed to async in the future

def rate_limit_public(request: Request, user: User | None = Depends(get_optional_current_user)):
    if not user:
        identifier = f"ip:{get_client_ip(request)}"
    else:
        identifier = f"user:{user.id}"

    key = f"rate_limit:{identifier}"

    # count = await redis_client.incr(key) 
    count = redis_client.incr(key)

    if count == 1:
        # await redis_client.expire(key, 60)  # 1 minute window
        redis_client.expire(key, 60)  # 1 minute window

    if count > 10:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again in few minutes.")


def rate_limit_private(user: User = Depends(get_current_user)):
    key = f"rate_limit:user:{user.id}"

    # count = await redis_client.incr(key)
    count = redis_client.incr(key)

    if count == 1:
        # await redis_client.expire(key, 60)  # 1 minute window
        redis_client.expire(key, 60)  # 1 minute window

    if count > 60:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again in few minutes.")
    
    
def rate_limit_auth(request: Request, user: User | None = Depends(get_optional_current_user)):
    if not user:
        identifier = f"ip:{get_client_ip(request)}"
    else:
        identifier = f"user:{user.id}"

    key = f"rate_limit:{identifier}"

    # count = await redis_client.incr(key)
    count = redis_client.incr(key)

    if count == 1:
        # await redis_client.expire(key, 60)  # 1 minute window
        redis_client.expire(key, 60)  # 1 minute window

    if count > 5:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again in few minutes.")
    

def get_client_ip(request: Request):
    xff = request.headers.get("X-Forwarded-For")

    if xff:
        return xff.split(",")[0].strip()
    
    return request.client.host