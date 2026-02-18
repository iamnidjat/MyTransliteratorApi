from pydantic import BaseModel

class SuccessfulTransliteration(BaseModel):
    original_text: str
    result_text: str
    response_code: int = 200 # default value
    response_message: str = "success" # default value