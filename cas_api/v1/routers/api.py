from fastapi import APIRouter

from cas_api.v1.routers import (
    analysis_interests,
    analysis_sentiments,
    analysis_similarity,
    visualizer_analysis_value,
    visualizer_quantity
)

api_router = APIRouter()

analysis_router = APIRouter()
analysis_router.include_router(analysis_interests.router, prefix="/interests", tags=["analysis_interests"])
analysis_router.include_router(analysis_sentiments.router, prefix="/sentiments", tags=["analysis_sentiments"])
analysis_router.include_router(analysis_similarity.router, prefix="/similarity", tags=["analysis_similarity"])

visualizer_router = APIRouter()
visualizer_router.include_router(visualizer_analysis_value.router, prefix="/analysis_value", tags=["visualizer_analysis_value"])
visualizer_router.include_router(visualizer_quantity.router, prefix="/quantity", tags=["visualizer_quantity"])

api_router.include_router(analysis_router, prefix="/analysis")
api_router.include_router(visualizer_router, prefix="/visualizer")
