from app.utils.custom_response_codes import ResponseCode


class AppException(Exception):
    def __init__(self, business_code: ResponseCode, http_status: int, message: str | None = None):
        self.business_code = business_code
        self.http_status = http_status
        self.message = message or business_code.value

        super().__init__(self.message)