from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.api.schemas.auth import Authenticate, AuthenticatedUser, ChangePassword, Login, SignUp, SuccessfulAuthentication, SuccessfulPwdChange, TokenRefreshResponse
from app.auth.jwt_handler import create_access_token, create_refresh_token, decode_token
from app.auth.security import hash_password, hash_token, verify_password
from app.core.models import User
from passlib.context import CryptContext

from app.core.models.refresh_token import RefreshToken
from app.auth.jwt_based_blacklist import blacklist
from app.exceptions.handlers import AppException
from app.repositories.auth_repository import create_user, create_token, soft_delete
from app.utils.custom_response_codes import MESSAGES, ResponseCode
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

load_dotenv()
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

def authenticate(loginCredentials: Login,  db: Session) -> SuccessfulAuthentication:
    user = db.query(User).filter(User.name == loginCredentials.username).first()

    if not user:
        # raise AppException(ResponseCode.USER_NOT_FOUND, http_status=404)
        logger.warning("Authentication failed: user not found", extra={
            "username": loginCredentials.username
        })
        raise AppException(ResponseCode.INVALID_CREDENTIALS, http_status=401) # for better security

    if not verify_password(loginCredentials.password, user.hashed_password):
        # raise AppException(ResponseCode.WRONG_PASSWORD, http_status=401)
        logger.warning("Authentication failed: invalid password", extra={
            "username": loginCredentials.username
        })
        raise AppException(ResponseCode.INVALID_CREDENTIALS, http_status=401) # for better security

    auth = generate_auth_response(user)
    save_refresh_token(user.id, auth.refresh_token, db)

    logger.info("Authentication successful", extra={
        "user_id": user.id
    })

    return SuccessfulAuthentication(
        business_code=ResponseCode.SUCCESS,
        data=auth
    )

def signup(signUpCredentials: SignUp, db: Session) -> SuccessfulAuthentication:
    existing_user  = db.query(User).filter(User.email == signUpCredentials.email).first()

    if existing_user :
        logger.warning("Signup failed: user already exists", extra={
            "username": signUpCredentials.username
        })
        raise AppException(ResponseCode.USER_ALREADY_EXISTS, http_status=409)
    
    new_user = User(
        name = signUpCredentials.username,
        email = signUpCredentials.email,
        hashed_password = hash_password(signUpCredentials.password)
    )
    
    create_user(new_user, db)
    logger.info("User created", extra={"user_id": new_user.id})

    auth = generate_auth_response(new_user)
    save_refresh_token(new_user.id, auth.refresh_token, db)

    return SuccessfulAuthentication(
        business_code=ResponseCode.SUCCESS,
        data=auth
    )

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

def logout(user_id: int, token: str, db: Session) -> ResponseCode:
    logger.info("Logging out user", extra={"user_id": user_id})
    blacklist_access_token(token)
    return revoke_refresh_token(user_id, db)

def revoke_refresh_token(user_id: int, db: Session) -> ResponseCode:
    try:
        tokens = db.query(RefreshToken).filter(RefreshToken.user_id == user_id).all()

        if not tokens:
            logger.info("No refresh tokens found", extra={
                "user_id": user_id
            })
            return ResponseCode.LOGOUT_SUCCESSFUL # No tokens found — still okay to logout  

        logger.info("Revoking refresh tokens", extra={
            "user_id": user_id,
            "token_count": len(tokens)
        })
        for token in tokens:
            soft_delete(token)
        
        db.commit()
        return ResponseCode.LOGOUT_SUCCESSFUL
    except SQLAlchemyError as e:
        db.rollback()  # undo changes if something fails
        logger.exception("Error revoking refresh tokens", extra={
            "user_id": user_id
        })
        raise AppException(
            ResponseCode.SERVER_ERROR,
            http_status=500
        )

def blacklist_access_token(token: str) -> None:
    payload = decode_token(token)

    jti = payload["jti"]
    exp = payload["exp"]

    # calculate remaining lifetime
    ttl = exp - int(datetime.now(timezone.utc).timestamp())

    if ttl > 0:
        blacklist(jti, ttl) 

def save_refresh_token(user_id: int, token: str, db: Session) -> ResponseCode:
    try:
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        hashed_token = hash_token(token)
        refresh_token = RefreshToken(
            token=hashed_token,
            user_id=user_id,
            expires_at=expires_at
        )
        create_token(refresh_token, db)
        logger.info("Refresh token saved", extra={
            "user_id": user_id
        })
        return ResponseCode.SUCCESS
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Error saving refresh tokens", extra={
            "user_id": user_id
        })
        raise AppException(
            ResponseCode.SERVER_ERROR,
            http_status=500
        )

def refresh(refresh_token: str, db: Session) -> TokenRefreshResponse:
    hashed_token = hash_token(refresh_token)
    try:
        token_obj = db.query(RefreshToken).filter(
            RefreshToken.token == hashed_token,
            RefreshToken.expires_at > datetime.now(timezone.utc),
            RefreshToken.is_used == False,
            RefreshToken.is_revoked == False,
        ).first()

        if not token_obj:
            logger.warning("Invalid refresh token attempt")
            raise AppException(
                    ResponseCode.INVALID_TOKEN,
                    http_status=401
                )
        
        # marking old token as used 
        token_obj.is_used = True
        db.flush() # → UPDATE refresh_tokens SET is_used = true

        logger.info("Old refresh token marked as used", extra={
            "user_id": token_obj.user_id,
            "token_id": token_obj.id
        })

        user = token_obj.user
        new_access_token = create_access_token({"sub": str(user.id)})
        new_refresh_token = create_refresh_token()
        new_hashed_token = hash_token(new_refresh_token)

        new_refresh_token_obj = RefreshToken(
            token=new_hashed_token,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )

        create_token(new_refresh_token_obj, db)

        logger.info("Token refreshed", extra={
            "user_id": user.id
        })

        return TokenRefreshResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Error refreshing access token", extra={
            "user_id": user.id if user else None
        })
        raise AppException(
            ResponseCode.SERVER_ERROR,
            http_status=500
        )

def change_password(changePwd: ChangePassword, user: User, db: Session) -> SuccessfulPwdChange:
    if not user:
        logger.warning("Password change failed: user not found", extra={
            "user_id": user.id if user else None
        })
        raise AppException(ResponseCode.INVALID_ACCOUNT, http_status=401)

    if not verify_password(changePwd.pwd, user.hashed_password):
        logger.warning("Password change failed: invalid old password", extra={
            "user_id": user.id if user else None
        })
        raise AppException(ResponseCode.INVALID_OLD_PWD, http_status=401)
    
    if verify_password(changePwd.new_pwd, user.hashed_password):
        logger.warning("Password change failed: new password is the same as the old password", extra={
            "user_id": user.id if user else None
        })
        raise AppException(ResponseCode.NEW_PASSWORD_SAME_AS_OLD, http_status=400)

    user.hashed_password = hash_password(changePwd.new_pwd)
    db.commit()
    db.refresh(user)

    logger.info("Password changed", extra={
        "user_id": user.id
    })

    return SuccessfulPwdChange(
        response_code=ResponseCode.SUCCESSFUL_PWD_CHANGE,
        response_message=MESSAGES[ResponseCode.SUCCESSFUL_PWD_CHANGE],
        user_id=user.id,
        updated_at=datetime.now(timezone.utc)
    )