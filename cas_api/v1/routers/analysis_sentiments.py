from fastapi import APIRouter
from starlette import status

from cas_api.worker import cas_api_worker
from cas_shared.schemas.task import CasTask
from config import WorkerTasks

router = APIRouter()


@router.get(
    "/comments/region",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Получить сентимент анализ комментаторов продукта сгруппированный по регионам",
    summary="Commentators sentiments by region"
)
async def customer_sentiment_comments_region(product_name_id: str):
    task = cas_api_worker.send_task(WorkerTasks.analyser_sentiment_regionally_commentators, args=[product_name_id])
    return CasTask(task_id=task.id, task_status=task.status)


@router.get(
    "/reviews/region",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Получить сентимент анализ ревьюеров продукта сгруппированный по регионам",
    summary="Reviewers sentiments by region"
)
async def customer_sentiment_reviews_region(product_name_id: str):
    task = cas_api_worker.send_task(WorkerTasks.analyser_sentiment_regionally_reviewers, args=[product_name_id])
    return CasTask(task_id=task.id, task_status=task.status)


@router.get(
    "/comments/category",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Получить сентимент анализ комментаторов продукта сгруппированный по категориям",
    summary="Commentators sentiments by category"
)
async def customer_sentiment_comments_category(product_name_id: str):
    task = cas_api_worker.send_task(WorkerTasks.analyser_sentiment_category_commentators, args=[product_name_id])
    return CasTask(task_id=task.id, task_status=task.status)


@router.get(
    "/reviews/category",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Получить сентимент анализ ревьюеров продукта сгруппированный по категориям",
    summary="Reviewers sentiments by category"
)
async def customer_sentiment_reviews_category(product_name_id: str):
    task = cas_api_worker.send_task(WorkerTasks.analyser_sentiment_category_reviewers, args=[product_name_id])
    return CasTask(task_id=task.id, task_status=task.status)
