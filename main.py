import logging as log

import yaml
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from customer_analysis_service.api.v1.routers.api import api_router

logger = log.getLogger('customer_analysis_service_logger')
log.basicConfig(level=log.INFO)

app = FastAPI()
app.include_router(api_router)


@app.get("/swagger.yaml")
async def get_swagger():
    openapi_schema = get_openapi(title="CAS API", version="1.0.0", routes=app.routes)
    with open("./docs/swagger.yaml", "w") as file:
        yaml.dump(openapi_schema, file)
    return openapi_schema
