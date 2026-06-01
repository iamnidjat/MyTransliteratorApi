from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.health_check_service import health_check, ready_check


router = APIRouter(
    prefix="/v1",
    tags=["health"],
)

@router.get("/health")
def health() -> dict:
    health_status = health_check()
    return health_status 

@router.get("/ready")
async def ready(db: Session = Depends(get_db)) -> dict:
    ready_status = await ready_check(db)
    return ready_status