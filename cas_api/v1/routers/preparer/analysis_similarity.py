from fastapi import APIRouter
from starlette import status

from cas_api.worker import cas_api_worker
from cas_shared.schemas.task import CasTask
from config import WorkerTasks


router = APIRouter()


@router.get(
    "/products",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Выполнения подготовки анализа сходства отзывов / комментариев продуктов",
    summary="Similarity analysis products preparer"
)
async def similarity_analysis_products_preparer(version_mark: str = "v1", is_override: bool = False):
    task = cas_api_worker.send_task(WorkerTasks.analyser_similarity_preparer_products, args=[version_mark, is_override])
    return CasTask(task_id=task.id, task_status=task.status)


@router.get(
    "/customers",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Выполнения подготовки анализа сходства отзывов / комментариев клиентов",
    summary="Similarity analysis customers preparer"
)
async def similarity_analysis_products_preparer(version_mark: str = "v1", is_override: bool = False):
    task = cas_api_worker.send_task(WorkerTasks.analyser_similarity_preparer_customers, args=[version_mark, is_override])
    return CasTask(task_id=task.id, task_status=task.status)
