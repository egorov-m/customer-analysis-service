from fastapi import APIRouter
from starlette import status

from cas_api.worker import cas_api_worker
from cas_shared.schemas.task import CasTask
from config import WorkerTasks

router = APIRouter()


@router.get(
    '/comments',
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Получить группировку по всем интересам комментаторов продукта.",
    summary="Commentators interests"
)
async def customer_interest_comments(product_name_id: str):
    task = cas_api_worker.send_task(WorkerTasks.analyser_interests_commentators, args=[product_name_id])
    return CasTask(task_id=task.id, task_status=task.status)


@router.get(
    "/reviews",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Получить группировку по всем интересам ревьюеров продукта.",
    summary="Reviewers interests"
)
async def customer_interests_reviews(product_name_id: str):
    task = cas_api_worker.send_task(WorkerTasks.analyser_interests_reviewers, args=[product_name_id])
    return CasTask(task_id=task.id, task_status=task.status)
