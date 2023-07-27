from fastapi import APIRouter, Depends
from sqlmodel import Session
from starlette import status

from customer_analysis_service.api.deps import get_db
from customer_analysis_service.api.v1.schemas.analysis import CustomersForAllCategoriesBaseAnalysis
from customer_analysis_service.services.analysis.interests import InterestAnalysisService

router = APIRouter()


@router.get(
    '/comments',
    response_model=list[CustomersForAllCategoriesBaseAnalysis],
    status_code=status.HTTP_200_OK,
    description="Получить группировку по всем интересам комментаторов продукта.",
    summary="Commentators interests"
)
async def customer_interest_comments(product_name_id: str, db: Session = Depends(get_db)):
    service: InterestAnalysisService = InterestAnalysisService(db)
    return service.get_group_customers_interest_for_all_categories_by_comments(product_name_id)


@router.get(
    "/reviews",
    response_model=list[CustomersForAllCategoriesBaseAnalysis],
    status_code=status.HTTP_200_OK,
    description="Получить группировку по всем интересам ревьюеров продукта.",
    summary="Reviewers interests"
)
async def customer_interests_reviews(product_name_id: str, db: Session = Depends(get_db)):
    service: InterestAnalysisService = InterestAnalysisService(db)
    return service.get_group_customers_interest_for_all_categories_by_reviews(product_name_id)
