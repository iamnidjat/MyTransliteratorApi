from app.core.models.transliteration_model import Transliteration
from sqlalchemy.orm import Session

def create(transliteration: Transliteration, db: Session):
    db.add(transliteration)
    db.commit()
    db.refresh(transliteration)

def save(db: Session):
    db.commit()

def get_active_by_user(user_id: int, db: Session):
    return (
        db.query(Transliteration)
        .filter(
            Transliteration.user_id == user_id,
            Transliteration.active == True
        )
        .all()
    )

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
    # db.delete(t_history)
    transliteration.active = False