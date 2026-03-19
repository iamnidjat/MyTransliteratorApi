from datetime import datetime

from app.core.models.transliteration_model import Transliteration
from sqlalchemy.orm import Session

def create(transliteration: Transliteration, db: Session):
    db.add(transliteration)
    db.commit()
    db.refresh(transliteration)

def save(db: Session):
    db.commit()

def get_active_by_user(page: int, page_size: int, user_id: int, db: Session):
    offset = (page - 1) * page_size
    return (
        db.query(Transliteration)
        .filter(
            Transliteration.user_id == user_id,
            Transliteration.active == True
        )
        .offset(offset)
        .limit(page_size)
        .all()
    )

def get_active_by_user_count(user_id: int, db: Session):
    total = (
        db.query(Transliteration)
        .filter(
            Transliteration.user_id == user_id,
            Transliteration.active == True
        )
        .count()
    )
    return total

def get_by_user_and_id(user_id: int, transliteration_id: int,  db: Session):
    return (
        db.query(Transliteration)
        .filter(
            Transliteration.user_id == user_id,
            Transliteration.id == transliteration_id,
            Transliteration.active == True
        ).first()
    )      

def soft_delete(transliteration: Transliteration):
    # db.delete(t_history) -> hard delete
    transliteration.active = False
    transliteration.revoked_at = datetime.utcnow()