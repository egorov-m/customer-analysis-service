from fastapi import APIRouter, Depends
from sqlmodel import Session

from customer_analysis_service.api.deps import get_db
from customer_analysis_service.api.v1.schemas.analysis import GroupRegionallyAllCustomerAnalysis, \
    CustomersForAllCategoriesAnalysis
from customer_analysis_service.services.analysis.sentiments import SentimentAnalysisService

router = APIRouter()


@router.get("/comments/region", response_model=list[GroupRegionallyAllCustomerAnalysis])
def customer_sentiment_comments_region(product_name_id: str, db: Session = Depends(get_db)):
    """
    Получить сентимент анализ сгруппированный по ругионам для всех комментариев клиентов выбранного продукта

    :визуализация Карта: https://plotly.com/python/scattermapbox/#basic-example-with-plotly-express
     (цветом показывать значения позитивности негативности от -1 до 1)

    :param product_name_id:
    :param db:
    :return:
    """
    service: SentimentAnalysisService = SentimentAnalysisService(db)
    return service.get_sentiment_analysis_group_regionally_all_customer_comments_product(product_name_id)


@router.get("/reviews/region", response_model=list[GroupRegionallyAllCustomerAnalysis])
def customer_sentiment_reviews_region(product_name_id: str, db: Session = Depends(get_db)):
    """
    Получить сентимент анализ сгруппированный по ругионам для всех отзывов клиентов выбранного продукта

    :визуализация Карта: https://plotly.com/python/scattermapbox/#basic-example-with-plotly-express
     (цветом показывать значения позитивности негативности от -1 до 1)

    :param product_name_id:
    :param db:
    :return:
    """
    service: SentimentAnalysisService = SentimentAnalysisService(db)
    return service.get_sentiment_analysis_group_regionally_all_customer_reviews_product(product_name_id)


@router.get("/comments/category", response_model=list[CustomersForAllCategoriesAnalysis])
def customer_sentiment_comments_category(product_name_id: str, db: Session = Depends(get_db)):
    """
    Получить сенитмент анализ комментариев клиентов указанного продукта сгруппированный по категориям

    визуализация: https://plotly.com/python/treemaps/ или https://plotly.com/python/sunburst-charts/

    :param product_name_id:
    :param db:
    :return:
    """
    service: SentimentAnalysisService = SentimentAnalysisService(db)
    return service.get_sentiment_analysis_customer_comments_product_grouped_by_category(product_name_id)


@router.get("/reviews/category", response_model=list[CustomersForAllCategoriesAnalysis])
def customer_sentiment_reviews_category(product_name_id: str, db: Session = Depends(get_db)):
    """
    Получить сенитмент анализ отзывов клиентов указанного продукта сгруппированный по категориям

    визуализация: https://plotly.com/python/treemaps/ или https://plotly.com/python/sunburst-charts/

    :param product_name_id:
    :param db:
    :return:
    """
    service: SentimentAnalysisService = SentimentAnalysisService(db)
    return service.get_sentiment_analysis_customer_reviews_product_grouped_by_category(product_name_id)
