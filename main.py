import logging as log
from http import HTTPStatus

import uvicorn
import yaml
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from starlette.responses import JSONResponse

from customer_analysis_service.api.v1.exceptions.cas_api_error import CasError, CasErrorCode
from customer_analysis_service.api.v1.routers.api import api_router
from customer_analysis_service.api.v1.schemas.exception import CasErrorResponse
from customer_analysis_service.config import settings

logger = log.getLogger('customer_analysis_service_logger')
log.basicConfig(level=log.INFO)

app = FastAPI(title=f"{settings.PROJECT_NAME} API", openapi_url=f"{settings.API_V1_STR}/openapi.json")
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get(f"/swagger.yaml", include_in_schema=False)
async def get_swagger():
    openapi_schema = get_openapi(title=f"{settings.PROJECT_NAME} API", version="1.0.0", routes=app.routes)
    with open("./docs/swagger.yaml", "w") as file:
        yaml.dump(openapi_schema, file)
    return openapi_schema


@app.exception_handler(CasError)
async def videonet_exception_handler(request: Request, exc: CasError):
    return JSONResponse(
        status_code=int(exc.http_status_code),
        content=CasErrorResponse(
            message=exc.message,
            error_code=CasErrorCode(exc.error_code)
        ).dict()
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, ex: Exception):
    status = HTTPStatus.INTERNAL_SERVER_ERROR
    return JSONResponse(
        status_code=status.value, content={"message": status.name, "error_code": CasErrorCode.GENERIC_ERROR}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
