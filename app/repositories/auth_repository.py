from app.core.models.refresh_token import RefreshToken
from app.core.models.user_model import User
from sqlalchemy.orm import Session

def create_user(user: User, db: Session):
    db.add(user)
    db.commit()
    db.refresh(user)

def create_token(token: RefreshToken, db: Session):
    db.add(token)
    db.commit()
    db.refresh(token)


def soft_delete(token: RefreshToken):
    token.is_revoked = True
