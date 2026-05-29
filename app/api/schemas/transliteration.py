from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


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
    status: Literal[1, 2] = Field(..., description="1 = successfull, 2 = failed")

class SuccessfulTransliterationRemoval(BaseModel):
    original_text: str
    result_text: str
    response_code: int = 200 # default value
    response_message: str = "success"
    unrecognized_symbols: list[str] = []
    done_at: datetime
    status: Literal[1, 2] = Field(..., description="1 = successfull, 2 = failed")

class SuccessfulTransliterationHistoryRemoval(BaseModel):
    response_code: int = 200 # default value
    response_message: str = "success"
    done_at: datetime
    status: Literal[1, 2] = Field(..., description="1 = successfull, 2 = failed")

class TransliterationHistory(BaseModel):
    original_text: str
    result_text: str
    source_language: str
    target_language: str
    unrecognized_symbols: Optional[list[str]] = []
    response_code: int = 200
    response_message: str = "success"
    created_at: datetime
    status: Literal[1, 2] = Field(..., description="1 = successfull, 2 = failed")
    active: bool

class TransliterationHistoryListResponse(BaseModel):
    total: int
    history: list[TransliterationHistory]
