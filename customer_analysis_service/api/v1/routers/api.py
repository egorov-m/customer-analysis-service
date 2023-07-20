from fastapi import APIRouter

from customer_analysis_service.api.v1.routers import (
    analysis_interests,
    analysis_sentiments,
    analysis_similarity,
    visualizer_group_category
)

api_router = APIRouter()

analysis_router = APIRouter()
analysis_router.include_router(analysis_interests.router, prefix="/interests", tags=["analysis_interests"])
analysis_router.include_router(analysis_sentiments.router, prefix="/sentiments", tags=["analysis_sentiments"])
analysis_router.include_router(analysis_similarity.router, prefix="/similarity", tags=["analysis_similarity"])

visualizer_router = APIRouter()
visualizer_router.include_router(visualizer_group_category.router, prefix="/category", tags=["visualizer_category"])

api_router.include_router(analysis_router, prefix="/analysis")
api_router.include_router(visualizer_router, prefix="/visualizer")
