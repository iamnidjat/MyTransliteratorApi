from app.utils.custom_response_codes import ResponseCode


class AppException(Exception):
    def __init__(self, code: ResponseCode, http_status: int):
        self.code = code
        self.http_status = http_status