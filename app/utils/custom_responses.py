from fastapi.responses import JSONResponse

def custom_response(http_status: int, business_code: int, message: str, data: dict) -> JSONResponse:
    return JSONResponse(
        content={
            "business_code": business_code,
            "msg": message,
            "data": data
        },
        status_code=http_status # sets HTTP response code
    )