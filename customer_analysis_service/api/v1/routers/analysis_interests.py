from fastapi import APIRouter, Depends

from customer_analysis_service.api.v1.dependencies.database import get_db
from customer_analysis_service.db import Database
from customer_analysis_service.services.analysis.interests import InterestAnalysisService

router = APIRouter()


@router.get('/comments')
def customer_interest_comments(product_name_id: str, database: Database = Depends(get_db)):
    """
    Получить группировк по всем категориям (интересам по комментариям) по клиентам нашего продукта

    :param product_name_id:
    :param database:
    :return:
    """
    service: InterestAnalysisService = InterestAnalysisService(database)
    return {
        'version': 'v1',
        'data': service.get_group_customers_interest_for_all_categories_by_comments(product_name_id)
    }


@router.get('/reviews')
def customer_interests_reviews(product_name_id: str, database: Database = Depends(get_db)):
    """
    Получить группировк по всем категориям (интересам по отзывам) по клиентам нашего продукта

    :param product_name_id:
    :param database:
    :return:
    """
    service: InterestAnalysisService = InterestAnalysisService(database)
    return {
        'version': 'v1',
        'data': service.get_group_customers_interest_for_all_categories_by_reviews(product_name_id)
    }
