from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.api.schemas.transliteration import SuccessfulTransliterationCreation, TransliterationHistory, \
    SuccessfulTransliterationHistoryRemoval, SuccessfulTransliterationRemoval
from app.constants.transliteration import az_cyrillic_to_latin_lower, az_cyrillic_to_latin_upper, \
    az_latin_to_cyrillic_lower, az_latin_to_cyrillic_upper
from app.core.models.transliteration_model import Transliteration
from app.exceptions.handlers import AppException
from app.utils.custom_response_codes import ResponseCode


def from_cyrillic_to_latin_az(cyrillic_text: str, flag: bool, db: Session) -> SuccessfulTransliterationCreation:
    return _transliterate(cyrillic_text, az_cyrillic_to_latin_lower, az_cyrillic_to_latin_upper, flag, db)

def from_latin_to_cyrillic_az(cyrillic_text: str, flag: bool, db: Session) -> SuccessfulTransliterationCreation:
    return _transliterate(cyrillic_text, az_latin_to_cyrillic_lower, az_latin_to_cyrillic_upper, flag, db)

def _transliterate(text: str, mapping_lower: dict[str, str], mapping_upper: dict[str, str], flag: bool, db: Session) -> SuccessfulTransliterationCreation:
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
        translated_text=result_text
    )

    if flag:
        db.add(transliteration)
        db.commit()
        db.refresh(transliteration)

    return SuccessfulTransliterationCreation(
        original_text=text,
        result_text=result_text,
        response_code=200,
        response_message="success",
        unrecognized_symbols=unrecognized,
        created_at=datetime.utcnow(),
        status=1
    )

def get_user_transliteration_history(user_id: int, db: Session) -> List[TransliterationHistory]:
    t_histories = db.query(Transliteration).filter(Transliteration.user_id == user_id).all()

    result = []
    for t_history in t_histories:
        result.append(TransliterationHistory(
            original_text=t_history.original_text,
            result_text=t_history.result_text,
            unrecognized_symbols=t_history.unrecognized_symbols,
            created_at=t_history.created_at,
            status=t_history.status
        ))

    return result

# change to soft delete
def delete_transliteration_history(user_id: int, db: Session) -> SuccessfulTransliterationHistoryRemoval:
    t_histories = db.query(Transliteration).filter(Transliteration.user_id == user_id).all()

    for t_history in t_histories:
        db.delete(t_history)

    db.commit()

    return SuccessfulTransliterationHistoryRemoval(
        response_code=200,
        response_message="success",
        done_at=datetime.utcnow(),
        status=1
    )

# change to soft delete
def delete_single_transliteration(user_id: int, transliteration_id: int , db: Session) -> SuccessfulTransliterationRemoval:
    t_history = (
        db.query(Transliteration)
        .filter(
            Transliteration.user_id == user_id,
            Transliteration.id == transliteration_id
        )
        .first()
    )

    if not t_history:
        raise AppException(ResponseCode.TRANSLITERATION_NOT_FOUND, http_status=404)

    db.delete(t_history)
    db.commit()

    return SuccessfulTransliterationRemoval(
        original_text=t_history.original_text,
        result_text=t_history.result_text,
        response_code=200,
        response_message="success",
        unrecognized_symbols=t_history.unrecognized_symbols,
        done_at=datetime.utcnow(),
        status=1
    )
