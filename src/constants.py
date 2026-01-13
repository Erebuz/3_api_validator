from enum import Enum, IntEnum


class Gender(IntEnum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2


class ErrorMessage(Enum):
    BAD_REQUEST = "Bad Request"
    FORBIDDEN = "Forbidden"
    NOT_FOUND = "Not Found"
    INVALID_REQUEST = "Invalid Request"
    INTERNAL_ERROR = "Internal Server Error"


SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"

OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500

ERRORS = {
    400: ErrorMessage.BAD_REQUEST.value,
    403: ErrorMessage.FORBIDDEN.value,
    404: ErrorMessage.NOT_FOUND.value,
    422: ErrorMessage.INVALID_REQUEST.value,
    500: ErrorMessage.INTERNAL_ERROR.value,
}
