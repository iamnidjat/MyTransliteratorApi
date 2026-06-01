from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.redis import redis_client

# Used by Docker to check if the app process is alive
def health_check() -> dict:
    return {"status": "ok"}

# Used by Kubernetes / load balancers to check if the app can serve traffic
async def ready_check(db: Session) -> dict:
    try:
        db.execute("SELECT 1") # check whether database is alive
    except Exception:
        # logger.exception("Database is not available")
        raise HTTPException(status_code=503, detail="Database not ready")

    try:
        await redis_client.ping() # check whether redis is alive
    except Exception:
        # logger.exception("Redis is not available")
        raise HTTPException(status_code=503, detail="Redis not ready")

    return {"status": "ready"}