from datetime import datetime
from pydantic import BaseModel


class TransliterationRequest(BaseModel):
    text: str
    flag: bool = False # auth flag, if True -> authorized

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
    unrecognized_symbols: list[str] = []
    created_at: datetime
    status: int
