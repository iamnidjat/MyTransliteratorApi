from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.api.schemas.auth import Authenticate, AuthenticatedUser, Login, SignUp, SuccessfulPwdChange, TokenRefreshResponse
from app.auth.jwt_handler import create_access_token, create_refresh_token, decode_token
from app.auth.security import hash_password, verify_password
from app.core.models import User
from passlib.context import CryptContext

from app.core.models.refresh_token import RefreshToken
from app.exceptions.handlers import AppException
from app.utils.custom_response_codes import MESSAGES, ResponseCode
from dotenv import load_dotenv
import os

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

load_dotenv()
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

def authenticate(loginCredentials: Login,  db: Session) -> Authenticate:
    user = db.query(User).filter(User.name == loginCredentials.username).first()

    if not user:
        # raise AppException(ResponseCode.USER_NOT_FOUND, http_status=404)
        raise AppException(ResponseCode.INVALID_CREDENTIALS, http_status=401) # for better security

    if not verify_password(loginCredentials.password, user.hashed_password):
        # raise AppException(ResponseCode.WRONG_PASSWORD, http_status=401)
        raise AppException(ResponseCode.INVALID_CREDENTIALS, http_status=401) # for better security

    auth = generate_auth_response(user)
    save_refresh_token(user.id, auth.refresh_token, db)

    return auth

def signup(signUpCredentials: SignUp, db: Session) -> Authenticate:
    existing_user  = db.query(User).filter(User.name == signUpCredentials.username).first()

    if existing_user :
        raise AppException(ResponseCode.USER_ALREADY_EXISTS, http_status=409)
    
    new_user = User(
        name = signUpCredentials.username,
        email = signUpCredentials.email,
        hashed_password = hash_password(signUpCredentials.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    auth = generate_auth_response(new_user)
    save_refresh_token(new_user.id, auth.refresh_token, db)

    return auth


def generate_auth_response(user: User) -> Authenticate:
    token_data = {"sub": str(user.id)}

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

def logout(user_id: int, db: Session) -> ResponseCode:
    return revoke_refresh_token(user_id, db)

def revoke_refresh_token(user_id: int, db: Session) -> ResponseCode:
    try:
        tokens = db.query(RefreshToken).filter(RefreshToken.user_id == user_id).all()
        print(f"Revoking {len(tokens)} refresh tokens for user_id={user_id}")

        if not tokens:
            return ResponseCode.SUCCESS  # No tokens found — still okay to logout  

        for token in tokens:
            # db.delete(token)
            token.is_revoked = True
        
        db.commit()
        return ResponseCode.SUCCESS
    except SQLAlchemyError as e:
        db.rollback()  # undo changes if something fails
        print(f"Error revoking refresh tokens: {e}")
        raise AppException(
            ResponseCode.SERVER_ERROR,
            http_status=500
        )

def save_refresh_token(user_id: int, token: str, db: Session) -> ResponseCode:
    try:
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)
        print(f"Saved refresh token for user_id={user_id}, token={token}")
        return ResponseCode.SUCCESS
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error saving refresh token: {e}")
        raise AppException(
            ResponseCode.SERVER_ERROR,
            http_status=500
        )

def refresh(refresh_token: str, db: Session) -> TokenRefreshResponse:
    try:
        token_obj = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            RefreshToken.expires_at > datetime.utcnow(),
            RefreshToken.is_used == False,
            RefreshToken.is_revoked == False,
        ).first()

        if not token_obj:
            raise AppException(
                    ResponseCode.INVALID_TOKEN,
                    http_status=401
                )
        
        # marking old token as used 
        token_obj.is_used = True

        user = token_obj.user
        new_access_token = create_access_token({"sub": str(user.id)})
        new_refresh_token = create_refresh_token()

        new_refresh_token_obj = RefreshToken(
            token=new_refresh_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )

        db.add(new_refresh_token_obj)
        db.commit()
        db.refresh(new_refresh_token_obj)

        return TokenRefreshResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error refreshing access token: {e}")
        raise AppException(
            ResponseCode.SERVER_ERROR,
            http_status=500
        )

def change_password(email: str, pwd: str, new_pwd: str, db: Session) -> SuccessfulPwdChange:
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise AppException(ResponseCode.INVALID_ACCOUNT, http_status=404)

    if not verify_password(pwd, user.hashed_password):
        raise AppException(ResponseCode.INVALID_OLD_PWD, http_status=401)

    user.hashed_password = hash_password(new_pwd)
    db.commit()
    db.refresh(user)

    return SuccessfulPwdChange(
        response_code=ResponseCode.SUCCESSFUL_PWD_CHANGE,
        response_message=MESSAGES[ResponseCode.SUCCESSFUL_PWD_CHANGE],
        user_id=user.id,
        updated_at=datetime.utcnow()
    )