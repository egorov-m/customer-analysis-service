from fastapi import APIRouter
from fastapi_cache.decorator import cache
from starlette import status

from cas_api.worker import cas_api_worker
from cas_shared.schemas.analysis import AnalysisObjectType, SentimentAnalysisType, SimilarityAnalysisType
from cas_shared.schemas.task import CasTask
from config import WorkerTasks

router = APIRouter()


@router.get(
    "/interests",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Получить группировку по всем интересам.",
    summary="Interests"
)
@cache(expire=60)
async def interests_analysis(product_name_id: str, analysis_object_type: AnalysisObjectType):
    match analysis_object_type:
        case AnalysisObjectType.reviewers:
            task = cas_api_worker.send_task(WorkerTasks.analyser_interests_reviewers, args=[product_name_id])
            return CasTask(task_id=task.id, task_status=task.status)
        case AnalysisObjectType.commentators:
            task = cas_api_worker.send_task(WorkerTasks.analyser_interests_commentators, args=[product_name_id])
            return CasTask(task_id=task.id, task_status=task.status)


@router.get(
    "/sentiment",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Получить сентимент анализ.",
    summary="Sentiments"
)
@cache(expire=60)
async def sentiment_analysis(product_name_id: str,
                             analysis_object_type: AnalysisObjectType,
                             sentiment_analysis_type: SentimentAnalysisType):
    match analysis_object_type:
        case AnalysisObjectType.reviewers:
            match sentiment_analysis_type:
                case SentimentAnalysisType.category:
                    task = cas_api_worker.send_task(WorkerTasks.analyser_sentiment_category_reviewers, args=[product_name_id])
                    return CasTask(task_id=task.id, task_status=task.status)
                case SentimentAnalysisType.region:
                    task = cas_api_worker.send_task(WorkerTasks.analyser_sentiment_regionally_reviewers, args=[product_name_id])
                    return CasTask(task_id=task.id, task_status=task.status)
        case AnalysisObjectType.commentators:
            match sentiment_analysis_type:
                case SentimentAnalysisType.category:
                    task = cas_api_worker.send_task(WorkerTasks.analyser_sentiment_category_commentators, args=[product_name_id])
                    return CasTask(task_id=task.id, task_status=task.status)
                case SentimentAnalysisType.region:
                    task = cas_api_worker.send_task(WorkerTasks.analyser_sentiment_regionally_commentators, args=[product_name_id])
                    return CasTask(task_id=task.id, task_status=task.status)


@router.get(
    "/similarity",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Получить анализ схожести.",
    summary="Similarity analysis"
)
@cache(expire=60)
async def similarity_analysis(product_name_id: str,
                              analysis_object_type: AnalysisObjectType,
                              similarity_analysis_type: SimilarityAnalysisType):
    match analysis_object_type:
        case AnalysisObjectType.reviewers:
            match similarity_analysis_type:
                case SimilarityAnalysisType.category:
                    task = cas_api_worker.send_task(WorkerTasks.analyser_similarity_category_reviewers, args=[product_name_id])
                    return CasTask(task_id=task.id, task_status=task.status)
                case SimilarityAnalysisType.reputation:
                    task = cas_api_worker.send_task(WorkerTasks.analyser_similarity_reputation_reviewers, args=[product_name_id])
                    return CasTask(task_id=task.id, task_status=task.status)
        case AnalysisObjectType.commentators:
            match similarity_analysis_type:
                case SimilarityAnalysisType.category:
                    task = cas_api_worker.send_task(WorkerTasks.analyser_similarity_category_commentators, args=[product_name_id])
                    return CasTask(task_id=task.id, task_status=task.status)
                case SimilarityAnalysisType.reputation:
                    task = cas_api_worker.send_task(WorkerTasks.analyser_similarity_reputation_commentators, args=[product_name_id])
                    return CasTask(task_id=task.id, task_status=task.status)
