from fastapi import APIRouter
from starlette import status

from cas_api.worker import cas_api_worker
from cas_shared.schemas.task import CasTask
from config import WorkerTasks


router = APIRouter()


@router.get(
    "/reviewers",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Выполнения подготовки анализа настроений ревьюеров",
    summary="Sentiment analysis reviewers preparer"
)
async def sentiment_analysis_reviewers_preparer(version_mark: str = "v1", is_override: bool = False):
    task = cas_api_worker.send_task(WorkerTasks.analyser_sentiment_preparer_reviewers, args=[version_mark, is_override])
    return CasTask(task_id=task.id, task_status=task.status)


@router.get(
    "/commentators",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Выполнения подготовки анализа настроений комментаторов",
    summary="Sentiment analysis commentators preparer"
)
async def sentiment_analysis_commentators_preparer(version_mark: str = "v1", is_override: bool = False):
    task = cas_api_worker.send_task(WorkerTasks.analyser_sentiment_preparer_commentators, args=[version_mark, is_override])
    return CasTask(task_id=task.id, task_status=task.status)
