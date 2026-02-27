from fastapi.responses import JSONResponse

def custom_response(status_code: int, business_code: int, message: str, data: dict) -> JSONResponse:
    return JSONResponse(
        content={
            "status_code": business_code,
            "msg": message,
            "data": data
        },
        status_code=status_code # sets HTTP response code
    )