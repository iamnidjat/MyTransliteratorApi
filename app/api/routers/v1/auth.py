from fastapi import APIRouter, Body, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.api.schemas.auth import ChangePassword, Login, Logout, SignUp
from app.api.utils import set_auth_cookie
from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.core.models.user_model import User
from app.exceptions.handlers import AppException
from app.services.auth_service import authenticate, change_password, logout as revoke_user_tokens, refresh, signup
from app.utils.custom_response_codes import MESSAGES, ResponseCode
from app.utils.custom_responses import custom_response

router = APIRouter(
    prefix="/v1/auth",
    tags=["auth"],
)


@router.post("/login")
def login(request: Login, response: Response, db: Session = Depends(get_db)) -> JSONResponse:
    result = authenticate(request, db)

    auth_data = result.data

    response = custom_response(
        http_status=200,
        business_code=ResponseCode.LOGIN_SUCCESSFUL,
        message=MESSAGES[ResponseCode.LOGIN_SUCCESSFUL],
        data={
            "access_token": auth_data.access_token,
            "token_type": auth_data.token_type,
        }
    )

    # sets refresh token in cookie
    set_auth_cookie(response, auth_data.refresh_token)

    return response

@router.post("/signup")
def register(request: SignUp, response: Response, db: Session = Depends(get_db)) -> JSONResponse:
    result = signup(request, db)

    auth_data = result.data

    response = custom_response(
        http_status=200,
        business_code=ResponseCode.LOGIN_SUCCESSFUL,
        message=MESSAGES[ResponseCode.LOGIN_SUCCESSFUL],
        data={
            "access_token": auth_data.access_token,
            "token_type": auth_data.token_type,
        }
    )

    set_auth_cookie(response, auth_data.refresh_token)

    return response
    
@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> JSONResponse:
    revoke_user_tokens(current_user.id, db)

    return custom_response(
        http_status=200,
        business_code=ResponseCode.LOGOUT_SUCCESSFUL,
        message=MESSAGES[ResponseCode.LOGOUT_SUCCESSFUL],
        data=None
    )


@router.post("/refresh")
def refresh_token(request: Request, db: Session = Depends(get_db)) -> JSONResponse:
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise AppException(ResponseCode.NO_TOKEN_PROVIDED, http_status=401)

    token = refresh(refresh_token, db)

    if token.access_token is None or token.refresh_token is None:
        raise AppException(ResponseCode.INVALID_TOKEN, http_status=401)

    response = {
        "access_token": token.access_token,
        "token_type": "bearer"
    }

    # sends new refresh token as cookie again
    response = JSONResponse(content=response)
    response = set_auth_cookie(response, token.refresh_token, request)

    return response



@router.post("/changepwd")
def change_user_password(changePwd: ChangePassword, db: Session = Depends(get_db)) -> JSONResponse:
    code = change_password(changePwd, db)
    return custom_response(
        http_status=200,
        business_code=code.response_code,
        message=code.response_message,
        data={
            "user_id": code.user_id, 
            "updated_at": code.updated_at
        }
    )


