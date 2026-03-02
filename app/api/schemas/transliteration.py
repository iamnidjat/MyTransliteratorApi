from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TransliterationRequest(BaseModel):
    text: str

    # supports only one example
    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "text": "Салам, бугун һава сон дərəcə гөзəлдир!",
    #         }
    #     }

class SuccessfulTransliterationCreation(BaseModel):
    original_text: str
    result_text: str
    response_code: int = 200 # default value
    response_message: str = "success"
    unrecognized_symbols: list[str] = []
    created_at: datetime
    status: int

class SuccessfulTransliterationRemoval(BaseModel):
    original_text: str
    result_text: str
    response_code: int = 200 # default value
    response_message: str = "success"
    unrecognized_symbols: list[str] = []
    done_at: datetime
    status: int

class SuccessfulTransliterationHistoryRemoval(BaseModel):
    response_code: int = 200 # default value
    response_message: str = "success"
    done_at: datetime
    status: int

class TransliterationHistory(BaseModel):
    original_text: str
    result_text: str
    source_language: str
    target_language: str
    unrecognized_symbols: Optional[list[str]] = []
    response_code: int = 200
    response_message: str = "success"
    created_at: datetime
    status: int
    active: bool

class TransliterationHistoryListResponse(BaseModel):
    total: int
    history: list[TransliterationHistory]
