from fastapi import APIRouter, Security

from cas_api.deps import get_api_key
from cas_api.v1.routers import (
    products,
    pipeline,
    result,
    visualizer_analysis_value,
    visualizer_quantity,
    visualizer_histogram
)
from cas_api.v1.routers.provider import analysis_sentiments, analysis_interests, analysis_similarity
from cas_api.v1.routers.preparer import (
    analysis_sentiments as preparer_analysis_sentiments,
    analysis_similarity as preparer_analysis_similarity
)


api_router = APIRouter(dependencies=[Security(get_api_key)])

result_router = APIRouter()
result_router.include_router(result.router, prefix="/result", tags=["result"])

products_search_router = APIRouter()
products_search_router.include_router(products.router, prefix="/products", tags=["products"])

analysis_router = APIRouter()
analysis_router.include_router(analysis_interests.router, prefix="/provider/interests", tags=["analysis_interests"])
analysis_router.include_router(analysis_sentiments.router, prefix="/provider/sentiments", tags=["analysis_sentiments"])
analysis_router.include_router(analysis_similarity.router, prefix="/provider/similarity", tags=["analysis_similarity"])

analysis_router.include_router(preparer_analysis_sentiments.router, prefix="/preparer/sentiments", tags=["analysis_sentiments"])
analysis_router.include_router(preparer_analysis_similarity.router, prefix="/preparer/similarity", tags=["analysis_similarity"])

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
