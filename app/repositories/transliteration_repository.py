from datetime import datetime

from app.core.models.transliteration_model import Transliteration
from sqlalchemy.orm import Session

def create(transliteration: Transliteration, db: Session):
    db.add(transliteration)
    db.commit()
    db.refresh(transliteration)

def save(db: Session):
    db.commit()

def get_active_by_user(user_id: int, db: Session, page: int | None = None, page_size: int | None = None):
    query = (
        db.query(Transliteration)
        .filter(
            Transliteration.user_id == user_id,
            Transliteration.active == True
        )
        .order_by(Transliteration.created_at.desc(), Transliteration.id.desc())
    )

    if page is not None and page_size is not None:
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
    
    return query.all()

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