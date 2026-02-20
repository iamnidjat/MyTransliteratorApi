from sqlalchemy.orm import Session
from app.api.schemas.transliteration import SuccessfulTransliteration
from app.constants.transliteration import az_cyrillic_to_latin_lower, az_cyrillic_to_latin_upper, \
    az_latin_to_cyrillic_lower, az_latin_to_cyrillic_upper
from app.core.models.transliteration_model import Transliteration


def from_cyrillic_to_latin_az(cyrillic_text: str, db: Session):
    return _transliterate(cyrillic_text, az_cyrillic_to_latin_lower, az_cyrillic_to_latin_upper, db)

def from_latin_to_cyrillic_az(cyrillic_text: str, db: Session):
    return _transliterate(cyrillic_text, az_latin_to_cyrillic_lower, az_latin_to_cyrillic_upper, db)

def _transliterate(text: str, mapping_lower: dict[str, str], mapping_upper: dict[str, str], db: Session):
    result = []
    unrecognized = []

    for ch in text:
        if ch.isalpha():
            if ch in mapping_lower:
                result.append(mapping_lower.get(ch))
            elif ch in mapping_upper:
                result.append(mapping_upper.get(ch))
            else:
                result.append('?') # adding ? to specify that the symbol is unrecognized
                unrecognized.append(ch)
        else:
            result.append(ch)

    result_text = "".join(result)

    transliteration = Transliteration(
        user_id=1, # dummy data
        source_language="az",
        target_language="az",
        original_text=text,
        translated_text=result_text,
    )

    db.add(transliteration)
    db.commit()
    db.refresh(transliteration)

    return SuccessfulTransliteration(
        original_text=text,
        result_text=result_text,
        response_code=200,
        response_message="success",
        unrecognized_symbols=unrecognized
    )
