from fastapi import APIRouter, Depends
from sqlmodel import Session
from starlette import status

from customer_analysis_service.api.deps import get_db
from customer_analysis_service.api.v1.schemas.analysis import CustomerReputationAnalysisValue
from customer_analysis_service.services.analysis.similarity import SimilarityAnalysisService

router = APIRouter()


@router.get(
    "/comments/reputation",
    response_model=list[CustomerReputationAnalysisValue],
    status_code=status.HTTP_200_OK,
    description="Получить анализ схожести отзывов каждого клиента со значением репутации.",
    summary="Similarity comments customer analysis by product"
)
def get_customer_similarity_analysis_product_by_comments(product_name_id: str, db: Session = Depends(get_db)):
    service: SimilarityAnalysisService = SimilarityAnalysisService(db)
    return service.get_customer_by_reputation_similarity_analysis_product_by_comments(product_name_id)


@router.get(
    "/reviews/reputation",
    response_model=list[CustomerReputationAnalysisValue],
    status_code=status.HTTP_200_OK,
    description="Получить анализ схожести отзывов каждого клиента со значением репутации.",
    summary="Similarity reviews customer analysis by product"
)
def get_customer_similarity_analysis_product_by_reviews(product_name_id: str, db: Session = Depends(get_db)):
    service: SimilarityAnalysisService = SimilarityAnalysisService(db)
    return service.get_customer_by_reputation_similarity_analysis_product_by_reviews(product_name_id)
