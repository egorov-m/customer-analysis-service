from fastapi import APIRouter, Depends
from sqlmodel import Session

from customer_analysis_service.api.deps import get_db
from customer_analysis_service.services.analysis.similarity import SimilarityAnalysisService

router = APIRouter()


@router.get("/comments")
def get_customer_similarity_analysis_product_by_comments(product_name_id: str, db: Session = Depends(get_db)):
    """
    Получить значения сходства по всем отзывам каждого клиента (писал комментарий) продукта

    :визуализация https://plotly.com/python/histograms/#several-histograms-for-the-different-values-of-one-column
    по оси x - все клиенты
    по оси y - значения схежести по всем отзывам для каждого клиента
    урокни гистограммы - группировка по городам (city_ru или сity_en)

    :param product_name_id:
    :param db:
    :return:
    """
    service: SimilarityAnalysisService = SimilarityAnalysisService(db)
    return service.get_customer_similarity_analysis_product_by_comments(product_name_id)


@router.get("/reviews")
def get_customer_similarity_analysis_product_by_reviews(product_name_id: str, db: Session = Depends(get_db)):
    """
    Получить значения сходства по всем отзывам каждого клиента (писал отзыв) продукта

    :визуализация https://plotly.com/python/histograms/#several-histograms-for-the-different-values-of-one-column
    по оси x - все клиенты
    по оси y - значения схежести по всем отзывам для каждого клиента
    урокни гистограммы - группировка по городам (city_ru или сity_en)

    :param product_name_id:
    :param db:
    :return:
    """
    service: SimilarityAnalysisService = SimilarityAnalysisService(db)
    return service.get_customer_similarity_analysis_product_by_reviews(product_name_id)
