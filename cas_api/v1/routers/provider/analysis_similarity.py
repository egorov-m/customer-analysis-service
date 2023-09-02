from fastapi import APIRouter
from starlette import status

from cas_api.worker import cas_api_worker
from cas_shared.schemas.task import CasTask
from config import WorkerTasks

router = APIRouter()


@router.get(
    "/comments/reputation",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Получить анализ схожести отзывов каждого клиента со значением репутации.",
    summary="Similarity comments customer by reputation analysis by product"
)
async def get_customer_by_reputation_similarity_analysis_product_by_comments(product_name_id: str):
    task = cas_api_worker.send_task(WorkerTasks.analyser_similarity_reputation_commentators, args=[product_name_id])
    return CasTask(task_id=task.id, task_status=task.status)


@router.get(
    "/reviews/reputation",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Получить анализ схожести отзывов каждого клиента со значением репутации.",
    summary="Similarity reviews customer by reputation analysis by product"
)
async def get_customer_by_reputation_similarity_analysis_product_by_reviews(product_name_id: str):
    task = cas_api_worker.send_task(WorkerTasks.analyser_similarity_reputation_reviewers, args=[product_name_id])
    return CasTask(task_id=task.id, task_status=task.status)


@router.get(
    "/reviews/category",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Получить анализ схожести отзывов каждого клиента по категориям.",
    summary="Similarity reviews customer by category analysis by product"
)
async def get_customer_by_category_similarity_analysis_product_by_reviews(product_name_id: str):
    task = cas_api_worker.send_task(WorkerTasks.analyser_similarity_category_reviewers, args=[product_name_id])
    return CasTask(task_id=task.id, task_status=task.status)


@router.get(
    "/comments/category",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Получить анализ схожести комментариев каждого клиента по категориям.",
    summary="Similarity comments customer by category analysis by product"
)
async def get_customer_by_category_similarity_analysis_product_by_comments(product_name_id: str):
    task = cas_api_worker.send_task(WorkerTasks.analyser_similarity_category_commentators, args=[product_name_id])
    return CasTask(task_id=task.id, task_status=task.status)
