from datetime import datetime

from sqlalchemy.orm import Session

from app.api.schemas.auth import Authenticate, AuthenticatedUser, SuccessfulPwdChange
from app.auth.jwt_handler import create_access_token, create_refresh_token
from app.core.models import User
from passlib.context import CryptContext

from app.exceptions.handlers import AppException
from app.utils.custom_response_codes import MESSAGES, ResponseCode

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def authenticate(username, password, db: Session) -> Authenticate:
    user = db.query(User).filter(User.name == username).first()

    if not user:
        raise AppException(ResponseCode.USER_NOT_FOUND, http_status=404)

    if not pwd_context.verify(password, user.hashed_password):
        raise AppException(ResponseCode.WRONG_PASSWORD, http_status=401)

    token_data = {"sub": user.id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token()

    return Authenticate(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        user=AuthenticatedUser(
            id=user.id,
            name=user.name,
            email=user.email
        )
    )

def change_password(email: str, pwd: str, new_pwd: str, db: Session) -> SuccessfulPwdChange:
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise AppException(ResponseCode.INVALID_ACCOUNT, http_status=404)

    if not pwd_context.verify_password(pwd, user.password):
        raise AppException(ResponseCode.INVALID_OLD_PWD, http_status=401)

    user.password = pwd_context.hash(new_pwd)
    db.commit()
    db.refresh(user)

    return SuccessfulPwdChange(
        response_code=ResponseCode.SUCCESSFUL_PWD_CHANGE,
        response_message=MESSAGES[ResponseCode.SUCCESSFUL_PWD_CHANGE],
        user_id=user.id,
        updated_at=datetime.utcnow()
    )