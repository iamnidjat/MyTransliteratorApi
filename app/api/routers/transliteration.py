from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.schemas.transliteration import TransliterationRequest, TransliterationHistoryListResponse
from app.core.database import get_db
from app.services.transliteration_service import from_cyrillic_to_latin_az, from_latin_to_cyrillic_az, \
get_user_transliteration_history, delete_transliteration_history, delete_single_transliteration
from app.utils.custom_response_codes import ResponseCode
from app.utils.custom_responses import custom_response

router = APIRouter(
    prefix="/transliteration",
    tags=["transliteration"],
)

@router.post("/cyrillic-to-latin-az")
def transliterate_cyrillic_to_latin_az(request: TransliterationRequest, db: Session = Depends(get_db)):
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
def transliterate_latin_to_cyrillic_az(request: TransliterationRequest, db: Session = Depends(get_db)):
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
    "/users/{user_id}/history",
    response_model=TransliterationHistoryListResponse
)
def user_transliteration_history(user_id: int, db: Session = Depends(get_db)):
    return get_user_transliteration_history(user_id, db)

@router.delete("/{user_id}/all")
def remove_transliteration_history(user_id: int, db: Session = Depends(get_db)):
    try:
        result = delete_transliteration_history(user_id, db)
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

@router.delete("/{user_id}/{transliteration_id}")
def remove_single_transliteration(user_id: int, transliteration_id: int, db: Session = Depends(get_db)):
    try:
        result = delete_single_transliteration(user_id, transliteration_id, db)
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