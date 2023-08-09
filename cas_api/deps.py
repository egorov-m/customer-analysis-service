from fastapi import Security
from fastapi.security.api_key import APIKeyHeader
from starlette import status

from cas_shared.exceptions.cas_api_error import CasError, CasErrorCode
from config import settings

api_key_header = APIKeyHeader(name="X-API-Key", scheme_name="Cas API Key", auto_error=False)


async def get_api_key(header: str = Security(api_key_header)) -> str:
    if header == settings.CAS_API_MAIN_KEY:
        return header
    raise CasError(
        message="Invalid or missing API Key",
        error_code=CasErrorCode.UNAUTHORIZED_REQUEST,
        http_status_code=status.HTTP_401_UNAUTHORIZED
    )
