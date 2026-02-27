from enum import IntEnum

class ResponseCode(IntEnum):
    """
    Code ranges:
    1000–1999 → Success
    2000–2999 → Validation / Client Errors
    3000–3999 → Authentication / Authorization
    4000–4099 → Not Found
    4100–4199 → Permission / Operation Errors
    5000–5099 → Server Errors
    """

    # Success
    SUCCESS = 1000
    SUCCESSFUL_TRANSLITERATION_CREATION = 1100
    SUCCESSFUL_TRANSLITERATION_REMOVAL = 1101
    SUCCESSFUL_TRANSLITERATIONS_REMOVAL = 1102
    SUCCESSFUL_TRANSLITERATIONS_READING = 1103
    SUCCESSFUL_PWD_CHANGE = 1900

    # Validation / Client Errors
    INVALID_PARAMS = 2000
    INVALID_TOKEN = 2001
    INVALID_ACCOUNT = 2002
    WRONG_PASSWORD = 2003
    INVALID_OLD_PWD = 2004

    # Authentication / Authorization
    UNAUTHORIZED_OP = 3000

    # Not Found
    USER_NOT_FOUND = 4000
    TRANSLITERATION_NOT_FOUND = 4001

    # Permission / Business Restrictions
    SERVICE_ERROR = 4100

    # Server Errors
    SERVER_ERROR = 5000


MESSAGES: dict[ResponseCode, str] = {
    ResponseCode.SUCCESS:             "Success",
    ResponseCode.SUCCESSFUL_PWD_CHANGE: "Successful password change",
    ResponseCode.SUCCESSFUL_TRANSLITERATION_CREATION: "Successful transliteration creation",
    ResponseCode.SUCCESSFUL_TRANSLITERATION_REMOVAL: "Successful transliteration removal",
    ResponseCode.SUCCESSFUL_TRANSLITERATIONS_REMOVAL: "Successful transliterations removal",
    ResponseCode.SUCCESSFUL_TRANSLITERATIONS_READING: "Successful transliteration reading",
    ResponseCode.INVALID_PARAMS:      "Invalid request parameters",
    ResponseCode.INVALID_TOKEN:       "Invalid token",
    ResponseCode.INVALID_ACCOUNT:     "Invalid account",
    ResponseCode.INVALID_OLD_PWD:     "Invalid old password",
    ResponseCode.WRONG_PASSWORD:      "Wrong password",
    ResponseCode.SERVICE_ERROR:       "Service Error",
    ResponseCode.UNAUTHORIZED_OP:     "Unauthorized operation",
    ResponseCode.SERVER_ERROR:        "Server Error",
    ResponseCode.USER_NOT_FOUND:      "User not found",
    ResponseCode.TRANSLITERATION_NOT_FOUND: "Transliteration not found",
}