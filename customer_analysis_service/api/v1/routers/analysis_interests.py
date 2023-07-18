from fastapi import APIRouter, Depends
from sqlmodel import Session

from customer_analysis_service.api.deps import get_db
from customer_analysis_service.api.v1.schemas.analysis import CustomersForAllCategoriesBaseAnalysis
from customer_analysis_service.services.analysis.interests import InterestAnalysisService

router = APIRouter()


@router.get('/comments', response_model=list[CustomersForAllCategoriesBaseAnalysis])
def customer_interest_comments(product_name_id: str, db: Session = Depends(get_db)):
    """
    Получить группировк по всем категориям (интересам по комментариям) по клиентам нашего продукта

    :param product_name_id:
    :param db:
    :return:
    """
    service: InterestAnalysisService = InterestAnalysisService(db)
    return service.get_group_customers_interest_for_all_categories_by_comments(product_name_id)


@router.get('/reviews', response_model=list[CustomersForAllCategoriesBaseAnalysis])
def customer_interests_reviews(product_name_id: str, db: Session = Depends(get_db)):
    """
    Получить группировк по всем категориям (интересам по отзывам) по клиентам нашего продукта

    :param product_name_id:
    :param db:
    :return:
    """
    service: InterestAnalysisService = InterestAnalysisService(db)
    return service.get_group_customers_interest_for_all_categories_by_reviews(product_name_id)
