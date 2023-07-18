import logging as log

import uvicorn
import yaml
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from customer_analysis_service.api.v1.routers.api import api_router
from customer_analysis_service.config import settings

logger = log.getLogger('customer_analysis_service_logger')
log.basicConfig(level=log.INFO)

app = FastAPI(title=f"{settings.PROJECT_NAME} API", openapi_url=f"{settings.API_V1_STR}/openapi.json")
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get(f"/swagger.yaml")
async def get_swagger():
    openapi_schema = get_openapi(title=f"{settings.PROJECT_NAME} API", version="1.0.0", routes=app.routes)
    with open("./docs/swagger.yaml", "w") as file:
        yaml.dump(openapi_schema, file)
    return openapi_schema


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
