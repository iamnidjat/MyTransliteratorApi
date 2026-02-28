from fastapi import APIRouter, Body, Depends, File, Form, Path, Query, UploadFile
from sqlalchemy.orm import Session
from app.api.schemas.transliteration import TransliterationRequest, TransliterationHistoryListResponse
from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.core.models.user_model import User
from app.services.transliteration_service import from_cyrillic_to_latin_az, from_latin_to_cyrillic_az, \
get_user_transliteration_history, delete_transliteration_history, delete_single_transliteration
from app.utils.custom_response_codes import ResponseCode
from app.utils.custom_responses import custom_response

router = APIRouter(
    prefix="/transliteration",
    tags=["transliteration"],
)

@router.post("/cyrillic-to-latin-az")
def transliterate_cyrillic_to_latin_az(request: TransliterationRequest = Body(
        ...,
        examples={
            "non_authorized_case": {
                "summary": "Non authorized user's text",
                "description": "Transliteration when user is not logged in",
                "value": {
                    "text": "Салам, бугун һава сон дərəcə гөзəлдир!",
                    "flag": False
                }
            },
            "authorized_case": {
                "summary": "Authorized user's text",
                "description": "Transliteration when user logged in",
                "value": {
                    "text": "Салам, бугун һава сон дərəcə гөзəлдир!",
                    "flag": True
                }
            }
        }
    ), db: Session = Depends(get_db)):
    try:
        result = from_cyrillic_to_latin_az(request.text, request.flag, db)
        return custom_response(http_status=200,
                               business_code=result.response_code,
                               message=result.response_message,
                               data={
                                   "result_text": result.result_text,
                                   "unrecognized_symbols": result.unrecognized_symbols
                               })
    except Exception as e:
        # unexpected error
        return custom_response(
            http_status=500,
            business_code=ResponseCode.SERVER_ERROR,
            message="Internal server error",
            data={"error": str(e)}
        )

@router.post("/latin-to-cyrillic-az")
def transliterate_latin_to_cyrillic_az(request: TransliterationRequest = Body(
        ...,
        examples={
            "non_authorized_case": {
                "summary": "Non authorized user's text",
                "description": "Transliteration when user is not logged in",
                "value": {
                    "text": "Salam, bugün hava son dərəcə gözəldir!",
                    "flag": False
                }
            },
            "authorized_case": {
                "summary": "Authorized user's text",
                "description": "Transliteration when user logged in",
                "value": {
                    "text": "Salam, bugün hava son dərəcə gözəldir!",
                    "flag": True
                }
            }
        }
    ), db: Session = Depends(get_db)):
    try:
        result = from_latin_to_cyrillic_az(request.text, request.flag, db)
        return custom_response(http_status=200,
                               business_code=result.response_code,
                               message=result.response_message,
                               data={
                                   "result_text": result.result_text,
                                   "unrecognized_symbols": result.unrecognized_symbols
                               })
    except Exception as e:
        return custom_response(
            http_status=500,
            business_code=ResponseCode.SERVER_ERROR,
            message="Internal server error",
            data={"error": str(e)}
        )

@router.post("/cyrillic-to-latin-az/file")
async def transliterate_cyrillic_file(
    file: UploadFile = File(..., description="Upload a .txt file"),
    flag: bool = Form(..., description="True -> user authorized, otherwise False", example=True),
    db: Session = Depends(get_db)
):
    try:
        content = await file.read()
        text = content.decode("utf-8")

        result = from_cyrillic_to_latin_az(text, flag, db)
        return custom_response(http_status=200,
                               business_code=result.response_code,
                               message=result.response_message,
                               data={
                                   "result_text": result.result_text,
                                   "unrecognized_symbols": result.unrecognized_symbols
                               })
    except Exception as e:
        return custom_response(
            http_status=500,
            business_code=ResponseCode.SERVER_ERROR,
            message="Internal server error",
            data={"error": str(e)}
        )

@router.post("/latin-to-cyrillic-az/file")
async def transliterate_cyrillic_file(
    file: UploadFile = File(..., description="Upload a .txt file"),
    flag: bool = Form(..., description="True -> user authorized, otherwise False", example=True),
    db: Session = Depends(get_db)
):
    try:
        content = await file.read()
        text = content.decode("utf-8")

        result = from_latin_to_cyrillic_az(text, flag, db)
        return custom_response(http_status=200,
                               business_code=result.response_code,
                               message=result.response_message,
                               data={
                                   "result_text": result.result_text,
                                   "unrecognized_symbols": result.unrecognized_symbols
                               })
    except Exception as e:
        return custom_response(
            http_status=500,
            business_code=ResponseCode.SERVER_ERROR,
            message="Internal server error",
            data={"error": str(e)}
        )

# @router.get("/user_transliteration_history")
# def user_transliteration_history(user_id: int, db: Session = Depends(get_db)):
#     try:
#         results = get_user_transliteration_history(user_id, db)
#
#         return custom_response(
#             200,
#             "success",
#             results.model_dump()  # Pydantic v2
#             # result.dict()      # if using Pydantic v1
#         )
#     except Exception as e:
#         return custom_response(500, "Internal server error", {"error": str(e)})
@router.get(
    "/users/me/history",
    response_model=TransliterationHistoryListResponse
)
def user_transliteration_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_transliteration_history(current_user.id, db)

@router.delete("/me/all")
def remove_transliteration_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        result = delete_transliteration_history(current_user.id, db)
        return custom_response(http_status=200,
                               business_code=result.response_code,
                               message=result.response_message,
                               data={
                                    "done_at": result.done_at,
                                    "status": result.status
                               })
    except Exception as e:
        return custom_response(
            http_status=500,
            business_code=ResponseCode.SERVER_ERROR,
            message="Internal server error",
            data={"error": str(e)}
        )

@router.delete("/me/{transliteration_id}")
def remove_single_transliteration(transliteration_id: int = Path(..., description="transliteration id", example=1), 
                                current_user: User = Depends(get_current_user),                                 
                                db: Session = Depends(get_db)):
    try:
        result = delete_single_transliteration(current_user.id, transliteration_id, db)
        return custom_response(http_status=200,
                               business_code=result.response_code,
                               message=result.response_message,
                               data={
                                    "original_text": result.original_text,
                                    "result_text": result.result_text,
                                    "unrecognized_symbols": result.unrecognized_symbols,
                                    "created_at": result.created_at,
                                    "status": result.status,
                               })
    except Exception as e:
        return custom_response(
            http_status=500,
            business_code=ResponseCode.SERVER_ERROR,
            message="Internal server error",
            data={"error": str(e)}
        )