from enum import IntEnum
from http import HTTPStatus


class CasErrorCode(IntEnum):
    """
    Error codes of the Customer analysis service API.

    Ranges:
           0-1000: general errors
        1001-2000: tasks errors
        3001-4000: visualizer errors
        4001-5000: analysis shaper errors
    """

    # 0-1000: general errors
    GENERIC_ERROR = 0

    UNAUTHORIZED_REQUEST = 401
    TOO_MANY_REQUESTS = 429

    # 1001-2000: tasks errors
    TASK_RETRY_ERROR = 1003
    TASK_FAILURE_ERROR = 1004
    TASK_NOT_FOUND_ERROR = 1404

    # 3001-4000: visualizer errors
    VISUALIZATION_TYPE_ERROR = 3001

    # 4001-5000: analysis shaper errors
    ANALYSIS_SHAPER_ERROR = 4001


class CasError(Exception):
    """Base class for Customer Analysis Service exceptions."""

    message: str
    error_code: int
    http_status_code: HTTPStatus

    def __init__(self,
                 message: str,
                 error_code: CasErrorCode,
                 http_status_code: HTTPStatus = HTTPStatus.BAD_REQUEST,
                 *args):
        super().__init__(message, error_code, http_status_code, *args)
        self.message = message
        self.error_code = error_code
        self.http_status_code = http_status_code

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(message='{self.message}', error_code={self.error_code}, http_status_code={self.http_status_code})"
