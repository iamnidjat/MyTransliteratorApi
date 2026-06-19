from app.core.redis import redis_client

def blacklist(jti: str, expires_in_seconds: int):
    redis_client.set(
        f"blacklist:jti:{jti}",
        "revoked",
        ex=expires_in_seconds
    )

def is_token_blacklisted(jti: str) -> bool:
    return redis_client.get(f"blacklist:jti:{jti}") is not None