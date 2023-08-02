from fastapi import APIRouter, Depends
from sqlmodel import Session
from starlette import status

from cas_api.deps import get_db
from cas_shared.schemas.analysis import GroupRegionallyAllCustomerAnalysis, \
    CustomersForAllCategoriesAnalysis
from cas_worker.services.provider.sentiment import SentimentAnalysisProvider

router = APIRouter()


@router.get(
    "/comments/region",
    response_model=list[GroupRegionallyAllCustomerAnalysis],
    status_code=status.HTTP_200_OK,
    description="Получить сентимент анализ комментаторов продукта сгруппированный по регионам",
    summary="Commentators sentiments by region"
)
async def customer_sentiment_comments_region(product_name_id: str, db: Session = Depends(get_db)):
    service: SentimentAnalysisProvider = SentimentAnalysisProvider(db)
    return service.get_sentiment_analysis_by_regionally_of_commentators(product_name_id)


@router.get(
    "/reviews/region",
    response_model=list[GroupRegionallyAllCustomerAnalysis],
    status_code=status.HTTP_200_OK,
    description="Получить сентимент анализ ревьюеров продукта сгруппированный по регионам",
    summary="Reviewers sentiments by region"
)
async def customer_sentiment_reviews_region(product_name_id: str, db: Session = Depends(get_db)):
    service: SentimentAnalysisProvider = SentimentAnalysisProvider(db)
    return service.get_sentiment_analysis_by_regionally_of_reviewers(product_name_id)


@router.get(
    "/comments/category",
    response_model=list[CustomersForAllCategoriesAnalysis],
    status_code=status.HTTP_200_OK,
    description="Получить сентимент анализ комментаторов продукта сгруппированный по категориям",
    summary="Commentators sentiments by category"
)
async def customer_sentiment_comments_category(product_name_id: str, db: Session = Depends(get_db)):
    service: SentimentAnalysisProvider = SentimentAnalysisProvider(db)
    return service.get_sentiment_analysis_by_category_of_commentators(product_name_id)


@router.get(
    "/reviews/category",
    response_model=list[CustomersForAllCategoriesAnalysis],
    status_code=status.HTTP_200_OK,
    description="Получить сентимент анализ ревьюеров продукта сгруппированный по категориям",
    summary="Reviewers sentiments by category"
)
async def customer_sentiment_reviews_category(product_name_id: str, db: Session = Depends(get_db)):
    service: SentimentAnalysisProvider = SentimentAnalysisProvider(db)
    return service.get_sentiment_analysis_by_category_of_reviewers(product_name_id)
