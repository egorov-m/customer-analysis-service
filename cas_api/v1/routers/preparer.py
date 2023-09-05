from fastapi import APIRouter
from starlette import status

from cas_api.worker import cas_api_worker
from cas_shared.schemas.analysis import AnalysisObjectType, AnalysisPrepareSimilarityObjectType
from cas_shared.schemas.task import CasTask
from config import WorkerTasks


router = APIRouter()


@router.get(
    "/sentiment",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Выполнения подготовки анализа настроений",
    summary="Sentiment analysis preparer"
)
async def sentiment_analysis(analysis_object_type: AnalysisObjectType,
                             version_mark: str = "v1",
                             is_override: bool = False):
    match analysis_object_type:
        case AnalysisObjectType.reviewers:
            task = cas_api_worker.send_task(WorkerTasks.analyser_sentiment_preparer_reviewers, args=[version_mark, is_override])
            return CasTask(task_id=task.id, task_status=task.status)
        case AnalysisObjectType.commentators:
            task = cas_api_worker.send_task(WorkerTasks.analyser_sentiment_preparer_commentators, args=[version_mark, is_override])
            return CasTask(task_id=task.id, task_status=task.status)


@router.get(
    "/similarity",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Выполнения подготовки анализа сходства",
    summary="Similarity analysis preparer"
)
async def similarity_analysis(analysis_object_type: AnalysisPrepareSimilarityObjectType,
                              version_mark: str = "v1",
                              is_override: bool = False):
    match analysis_object_type:
        case AnalysisPrepareSimilarityObjectType.products:
            task = cas_api_worker.send_task(WorkerTasks.analyser_similarity_preparer_products, args=[version_mark, is_override])
            return CasTask(task_id=task.id, task_status=task.status)
        case AnalysisPrepareSimilarityObjectType.customers:
            task = cas_api_worker.send_task(WorkerTasks.analyser_similarity_preparer_customers, args=[version_mark, is_override])
            return CasTask(task_id=task.id, task_status=task.status)
