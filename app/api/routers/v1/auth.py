from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from app.api.schemas.auth import ChangePassword, Login, Logout, SignUp
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
def login(request: Login, db: Session = Depends(get_db)):
    try:
        result = authenticate(request, db)

        auth_data = result.data

        return custom_response(
            http_status=200,
            business_code=ResponseCode.LOGIN_SUCCESSFUL,
            message=MESSAGES[ResponseCode.LOGIN_SUCCESSFUL],
            data={
                "access_token": auth_data.access_token,
                "token_type": auth_data.token_type,
            }
        )
    except AppException as e:
        return custom_response(
            http_status=e.http_status,
            business_code=e.business_code,
            message=str(e),
            data=None
        )
    except Exception as e:
        # unexpected error
        return custom_response(
            http_status=500,
            business_code=ResponseCode.SERVER_ERROR,
            message=MESSAGES[ResponseCode.SERVER_ERROR],
            data={"error": str(e)}
        )

@router.post("/signup")
def register(request: SignUp, db: Session = Depends(get_db)):
    try:
        result = signup(request, db)

        auth_data = result.data

        return custom_response(
            http_status=201,
            business_code=ResponseCode.SIGNUP_SUCCESSFUL,
            message=MESSAGES[ResponseCode.SIGNUP_SUCCESSFUL],
            data={
                "access_token": auth_data.access_token,
                "token_type": auth_data.token_type,
            }
        )
    except AppException as e:
        return custom_response(
            http_status=e.http_status,
            business_code=e.business_code,
            message=str(e),
            data=None
        )
    except Exception as e:
        # unexpected error
        return custom_response(
            http_status=500,
            business_code=ResponseCode.SERVER_ERROR,
            message=MESSAGES[ResponseCode.SERVER_ERROR],
            data={"error": str(e)}
        )
    
@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        revoke_user_tokens(current_user.id, db)

        return custom_response(
            http_status=200,
            business_code=ResponseCode.LOGOUT_SUCCESSFUL,
            message=MESSAGES[ResponseCode.LOGOUT_SUCCESSFUL],
            data=None
        )
    except AppException as e:
        return custom_response(
            http_status=e.http_status,
            business_code=e.code,
            message=str(e),
            data=None
        )
    except Exception as e:
        return custom_response(
            http_status=500,
            business_code=ResponseCode.SERVER_ERROR,
            message=MESSAGES[ResponseCode.SERVER_ERROR],
            data={"error": str(e)}
        )

# @router.post("/refresh")
# def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
#     try:
#         code = refresh(refresh_token, db)
#     except Exception as e:
#         # unexpected error
#         return custom_response(
#             http_status=500,
#             business_code=ResponseCode.SERVER_ERROR,
#             message="Internal server error",
#             data={"error": str(e)}
#         )


# @router.post("/changepwd")
# def change_user_password(changePwd: ChangePassword, db: Session = Depends(get_db)):
#     try:
#         code = change_password(changePwd, db)
#     except Exception as e:
#         # unexpected error
#         return custom_response(
#             http_status=500,
#             business_code=ResponseCode.SERVER_ERROR,
#             message="Internal server error",
#             data={"error": str(e)}
#         )
