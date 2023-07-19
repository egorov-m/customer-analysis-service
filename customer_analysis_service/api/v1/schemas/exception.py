from pydantic import BaseModel

from customer_analysis_service.api.v1.exceptions.cas_api_error import CasErrorCode


class CasErrorResponse(BaseModel):
    """The format of an error response from the Customer Analysis Service API."""

    error_code: CasErrorCode
    message: str
