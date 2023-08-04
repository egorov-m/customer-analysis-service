from fastapi import APIRouter, Depends
from sqlmodel import Session
from starlette import status

from cas_api.deps import get_db
from cas_shared.schemas.analysis import CustomerReputationAnalysisValue
from cas_worker.tests.provider.similarity import SimilarityAnalysisProvider

router = APIRouter()


@router.get(
    "/comments/reputation",
    response_model=list[CustomerReputationAnalysisValue],
    status_code=status.HTTP_200_OK,
    description="Получить анализ схожести отзывов каждого клиента со значением репутации.",
    summary="Similarity comments customer analysis by product"
)
async def get_customer_similarity_analysis_product_by_comments(product_name_id: str, db: Session = Depends(get_db)):
    service: SimilarityAnalysisProvider = SimilarityAnalysisProvider(db)
    return service.get_similarity_analysis_by_reputation_of_commentators(product_name_id)


@router.get(
    "/reviews/reputation",
    response_model=list[CustomerReputationAnalysisValue],
    status_code=status.HTTP_200_OK,
    description="Получить анализ схожести отзывов каждого клиента со значением репутации.",
    summary="Similarity reviews customer analysis by product"
)
async def get_customer_similarity_analysis_product_by_reviews(product_name_id: str, db: Session = Depends(get_db)):
    service: SimilarityAnalysisProvider = SimilarityAnalysisProvider(db)
    return service.get_similarity_analysis_by_reputation_of_reviewers(product_name_id)
