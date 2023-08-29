from typing import Annotated

from fastapi import APIRouter, Query
from starlette import status

from cas_api.worker import cas_api_worker
from cas_shared.schemas.analysis import CustomerReputationAnalysisValue
from cas_shared.schemas.task import CasTask
from cas_shared.schemas.visualizer import VisualizationType
from config import WorkerTasks

router = APIRouter()


@router.post(
    "",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Визуализировать сходство отзывов / комментариев, по значениям репутации. (для analysis_similarity_reputation)",
    summary="Visualize quantities by grouping by category"
)
async def visualize_similarity_by_reputation(data: list[CustomerReputationAnalysisValue],
                                             vis_type: VisualizationType,
                                             title: Annotated[str, Query(
                                                 description="Заголовок визаулизации аналитики",
                                                 min_length=3,
                                                 max_length=100)] = "Customer Analysis",
                                             title_object_count: Annotated[str, Query(
                                                 description="Обозначение количественного значения клиенты",
                                                 min_length=3,
                                                 max_length=50)] = "Count customers",
                                             title_analysis_value: Annotated[str, Query(
                                                 description="Обозначение значения анализа настроение / схожесть / т.п.",
                                                 min_length=3,
                                                 max_length=50)] = "Analysis value",
                                             # title_quantity: Annotated[str, Query(
                                             #     description="Обозначение количественного значения клиенты / отзывы / комментарии",
                                             #     min_length=3,
                                             #     max_length=50)] = "Count customers"
                                             ):
    task = cas_api_worker.send_task(WorkerTasks.visualizer_histogram_visualize,
                                    args=[[dict(item) for item in data],
                                          title,
                                          title_object_count,
                                          title_analysis_value,
                                          vis_type])
    return CasTask(task_id=task.id, task_status=task.status)
