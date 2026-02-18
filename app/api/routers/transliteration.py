from fastapi import APIRouter

from app.services.transliteration_service import from_cyrillic_to_latin_az
from app.utils.custom_responses import custom_response

router = APIRouter(
    prefix="/transliteration",
    tags=["transliteration"],
)

@router.post("/")
def transliterate(text: str):
    try:
        result = from_cyrillic_to_latin_az(text)
        return custom_response(result.response_code, result.response_message, result.result_text)
    except Exception as e:
        # unexpected error
        return custom_response(500, "Internal server error", {"error": str(e)})