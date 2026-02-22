from sqlalchemy.orm import Session

from app.auth.jwt_handler import create_access_token, create_refresh_token
from app.core.models import User
from passlib.context import CryptContext

from app.exceptions.handlers import AppException
from app.utils.custom_response_codes import ResponseCode

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def authenticate(username, password, db: Session):
    user = db.query(User).filter(User.name == username).first()

    if not user:
        raise AppException(ResponseCode.USER_NOT_FOUND, http_status=404)

    if not pwd_context.verify(password, user.hashed_password):
        raise AppException(ResponseCode.WRONG_PASSWORD, http_status=401)

    token_data = {"sub": user.id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }