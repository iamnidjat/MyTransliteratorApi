from app.api.schemas.transliteration import SuccessfulTransliteration
from app.constants.transliteration import az_cyrillic_to_latin


def from_cyrillic_to_latin_az(cyrillic_text: str):
    result = []

    for ch in cyrillic_text:
        # dict.get avoids KeyError; fallback to the original character (second ch)
        latin_char = az_cyrillic_to_latin.get(ch, ch)
        result.append(latin_char)

    result_text = "".join(result)

    return SuccessfulTransliteration(
        original_text=cyrillic_text,
        result_text=result_text,
        response_code=200,
        response_message="success"
    )