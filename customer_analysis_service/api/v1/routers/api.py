from fastapi import APIRouter

from customer_analysis_service.api.v1.routers import analysis_interests, analysis_sentiments

api_router = APIRouter()
api_router.include_router(analysis_interests.router, prefix='/analysis_interests', tags=['analysis_interests'])
api_router.include_router(analysis_sentiments.router, prefix='/analysis_sentiments', tags=['analysis_sentiments'])
