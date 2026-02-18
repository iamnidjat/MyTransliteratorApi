from app.api.schemas.transliteration import SuccessfulTransliteration
from app.constants.transliteration import az_cyrillic_to_latin, az_latin_to_cyrillic


def from_cyrillic_to_latin_az(cyrillic_text: str):
    return _transliterate(cyrillic_text, az_cyrillic_to_latin)

def from_latin_to_cyrillic_az(cyrillic_text: str):
    return _transliterate(cyrillic_text, az_latin_to_cyrillic)

def _transliterate(text: str, mapping: dict[str, str]):
    result = []
    unrecognized = []

    for ch in text:
        if ch.isalpha():
            if ch in mapping:
                result.append(mapping.get(ch))
            else:
                result.append('?') # adding ? to specify that the symbol is unrecognized
                unrecognized.append(ch)
        else:
            result.append(ch)

    result_text = "".join(result)

    return SuccessfulTransliteration(
        original_text=text,
        result_text=result_text,
        response_code=200,
        response_message="success",
        unrecognized_symbols=unrecognized
    )
