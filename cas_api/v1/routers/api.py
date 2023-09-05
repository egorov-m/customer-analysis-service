from fastapi import APIRouter, Security

from cas_api.deps import get_api_key
from cas_api.v1.routers import (
    scraper,
    pipeline,
    result,
    visualizer_analysis_value,
    visualizer_quantity,
    visualizer_histogram
)
from cas_api.v1.routers.provider import router as provider_router
from cas_api.v1.routers.preparer import router as preparer_router


api_router = APIRouter(dependencies=[Security(get_api_key)])

result_router = APIRouter()
result_router.include_router(result.router, prefix="/result", tags=["result"])

products_search_router = APIRouter()
products_search_router.include_router(scraper.router, prefix="/scraper", tags=["scraper"])

analysis_router = APIRouter()
analysis_router.include_router(provider_router, prefix="/provider", tags=["analysis_provider"])

analysis_router.include_router(preparer_router, prefix="/preparer", tags=["analysis_preparer"])

visualizer_router = APIRouter()
visualizer_router.include_router(visualizer_analysis_value.router, prefix="/analysis_value", tags=["visualizer_analysis_value"])
visualizer_router.include_router(visualizer_quantity.router, prefix="/quantity", tags=["visualizer_quantity"])
visualizer_router.include_router(visualizer_histogram.router, prefix="/histogram", tags=["visualizer_histogram"])

pipeline_router = APIRouter()
pipeline_router.include_router(pipeline.router, prefix="/shaper", tags=["pipeline_shaper"])

api_router.include_router(result_router)
api_router.include_router(products_search_router)
api_router.include_router(analysis_router, prefix="/analysis")
api_router.include_router(visualizer_router, prefix="/visualizer")
api_router.include_router(pipeline_router, prefix="/pipeline")
