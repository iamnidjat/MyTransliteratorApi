from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.schemas.transliteration import TransliterationRequest
from app.core.database import get_db
from app.services.transliteration_service import from_cyrillic_to_latin_az, from_latin_to_cyrillic_az
from app.utils.custom_responses import custom_response

router = APIRouter(
    prefix="/transliteration",
    tags=["transliteration"],
)

@router.post("/cyrillic-to-latin-az")
def transliterate_cyrillic_to_latin_az(request: TransliterationRequest, db: Session = Depends(get_db)):
    try:
        result = from_cyrillic_to_latin_az(request.text, request.flag, db)
        return custom_response(result.response_code,
                               result.response_message,
                               {
                                   "result_text": result.result_text,
                                   "unrecognized_symbols": result.unrecognized_symbols
                               })
    except Exception as e:
        # unexpected error
        return custom_response(500, "Internal server error", {"error": str(e)})

@router.post("/latin-to-cyrillic-az")
def transliterate_latin_to_cyrillic_az(request: TransliterationRequest, db: Session = Depends(get_db)):
    try:
        result = from_latin_to_cyrillic_az(request.text, request.flag, db)
        return custom_response(result.response_code,
                               result.response_message,
                               {
                                   "result_text": result.result_text,
                                   "unrecognized_symbols": result.unrecognized_symbols
                               })
    except Exception as e:
        return custom_response(500, "Internal server error", {"error": str(e)})