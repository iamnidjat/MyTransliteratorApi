from datetime import datetime
import json
from sqlalchemy.orm import Session
from app.api.schemas.transliteration import SuccessfulTransliterationCreation, TransliterationHistory, \
    SuccessfulTransliterationHistoryRemoval, SuccessfulTransliterationRemoval, TransliterationHistoryListResponse
from app.constants.transliteration import az_cyrillic_to_latin_lower, az_cyrillic_to_latin_upper, \
    az_latin_to_cyrillic_lower, az_latin_to_cyrillic_upper
from app.core.models.transliteration_model import Transliteration
from app.core.models.user_model import User
from app.exceptions.handlers import AppException
from app.utils.custom_response_codes import MESSAGES, ResponseCode
from app.repositories.transliteration_repository import create, get_active_by_user_count, save, get_active_by_user, get_by_user_and_id, soft_delete
from app.core.redis import redis_client
import time

def from_cyrillic_to_latin_az(cyrillic_text: str, current_user: User | None, db: Session) -> SuccessfulTransliterationCreation:
    return _transliterate(cyrillic_text, az_cyrillic_to_latin_lower, az_cyrillic_to_latin_upper, current_user, db)

def from_latin_to_cyrillic_az(cyrillic_text: str, current_user: User | None, db: Session) -> SuccessfulTransliterationCreation:
    return _transliterate(cyrillic_text, az_latin_to_cyrillic_lower, az_latin_to_cyrillic_upper, current_user, db)

def _transliterate(text: str, mapping_lower: dict[str, str], mapping_upper: dict[str, str], current_user: User | None, db: Session) -> SuccessfulTransliterationCreation:
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
                # result.append(ch) approach 2
        else:
            result.append(ch)

    result_text = "".join(result)

    if current_user:
        transliteration = Transliteration(
            user_id=current_user.id,
            source_language="az",
            target_language="az",
            original_text=text,
            translated_text=result_text,
            created_at=datetime.utcnow(),
            status=1,
            active=True,
        )
        
        create(transliteration, db)
        _invalidate_history_cache(current_user.id)

    return SuccessfulTransliterationCreation(
        original_text=text,
        result_text=result_text,
        response_code=ResponseCode.SUCCESSFUL_TRANSLITERATION_CREATION,
        response_message=MESSAGES[ResponseCode.SUCCESSFUL_TRANSLITERATION_CREATION],
        unrecognized_symbols=unrecognized,
        created_at=datetime.utcnow(),
        status=1
    )

def get_user_transliteration_history(page: int, page_size: int, user_id: int, db: Session) -> TransliterationHistoryListResponse:
    cache_key = f"user:{user_id}:transliteration_history"

    # 1️⃣ Try to get from Redis
    start_redis = time.time()
    # getting from Redis
    cached = redis_client.get(cache_key)
    redis_time = time.time() - start_redis

    if cached:
        print(f"Redis fetch time: {redis_time:.6f}s")
        # if exists - returns cached data
        return TransliterationHistoryListResponse.model_validate_json(cached)
    
    # 2️⃣ Fetch from DB
    start_db = time.time()
    t_histories = get_active_by_user(page, page_size, user_id, db)
    t_histories_length = get_active_by_user_count(user_id, db)
    db_time = time.time() - start_db
    print(f"DB fetch time: {db_time:.6f}s")

    # DB fetch: 0.047953s for 2 records → may increase with more records
    # Redis fetch: 0.008229s for 2 records → almost constant, very fast caching

    result = []
    for t_history in t_histories:
        result.append(TransliterationHistory(
            original_text=t_history.original_text,
            result_text=t_history.translated_text,
            source_language=t_history.source_language,
            target_language=t_history.target_language,
            unrecognized_symbols=t_history.unrecognized_symbols,
            created_at=t_history.created_at,
            status=t_history.status,
            active=t_history.active,
            response_code=ResponseCode.SUCCESSFUL_TRANSLITERATION_REMOVAL,
            response_message=MESSAGES[ResponseCode.SUCCESSFUL_TRANSLITERATION_REMOVAL],
        ))

    response = TransliterationHistoryListResponse(
        total=t_histories_length,
        history=result
    )    
    
    # cache the result for 5 minutes (balanced time; history can change quickly)
    redis_client.set(cache_key, response.model_dump_json(), ex=300) # converting the Pydantic model to a Python dict, then
                                                                    # converting the dict to JSON string, which Redis can store

    return response

def delete_transliteration_history(user_id: int, db: Session) -> SuccessfulTransliterationHistoryRemoval:
    t_histories = get_active_by_user(user_id, db)

    for t_history in t_histories:
        soft_delete(t_history)

    save(db)
    _invalidate_history_cache(user_id)

    return SuccessfulTransliterationHistoryRemoval(
        response_code=ResponseCode.SUCCESSFUL_TRANSLITERATIONS_REMOVAL,
        response_message=MESSAGES[ResponseCode.SUCCESSFUL_TRANSLITERATIONS_REMOVAL],
        done_at=datetime.utcnow(),
        status=1
    )

def delete_single_transliteration(user_id: int, transliteration_id: int , db: Session) -> SuccessfulTransliterationRemoval:
    t_history = get_by_user_and_id(user_id, transliteration_id, db)

    if not t_history:
        raise AppException(ResponseCode.TRANSLITERATION_NOT_FOUND, http_status=404)

    soft_delete(t_history)
    save(db)
    _invalidate_history_cache(user_id)
    
    return SuccessfulTransliterationRemoval(
        original_text=t_history.original_text,
        result_text=t_history.result_text,
        response_code=ResponseCode.SUCCESSFUL_TRANSLITERATION_REMOVAL,
        response_message=MESSAGES[ResponseCode.SUCCESSFUL_TRANSLITERATION_REMOVAL],
        unrecognized_symbols=t_history.unrecognized_symbols,
        done_at=datetime.utcnow(),
        status=1
    )

def _invalidate_history_cache(user_id: int):
    cache_key = f"user:{user_id}:transliteration_history"
    redis_client.delete(cache_key)