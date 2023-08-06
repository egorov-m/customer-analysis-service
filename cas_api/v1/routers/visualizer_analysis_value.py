from typing import Annotated

from fastapi import APIRouter, Query
from starlette import status

from cas_api.worker import cas_api_worker
from cas_shared.schemas.analysis import CustomersForAllCategoriesAnalysis,\
    GroupRegionallyAllCustomerAnalysis
from cas_shared.schemas.task import CasTask
from cas_shared.schemas.visualizer import VisualizationType
from config import WorkerTasks

router = APIRouter()


@router.post(
    "/category",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Визуализировать значения анализа, группируя по всем категориям. (для analysis_sentiments category)",
    summary="Visualize analysis values by grouping by category"
)
async def visualize_analysis_value_by_groupings_by_category(data: list[CustomersForAllCategoriesAnalysis],
                                                            vis_type: VisualizationType,
                                                            title: Annotated[str, Query(
                                                                description="Заголовок визаулизации аналитики",
                                                                min_length=3,
                                                                max_length=100)] = "Customer Analysis",
                                                            title_object_count: Annotated[str, Query(
                                                                description="Обозначение количественного значения клиенты / отзывы / комментарии",
                                                                min_length=3,
                                                                max_length=50)] = "Count customers",
                                                            title_analysis_value: Annotated[str, Query(
                                                                description="Обозначение значения анализа настроение / схожесть / т.п.",
                                                                min_length=3,
                                                                max_length=50)] = "Analysis value",
                                                            ):
    task = cas_api_worker.send_task(WorkerTasks.visualizer_group_visualize_analysis_value,
                                    args=[[dict(item) for item in data], title, title_object_count, title_analysis_value,
                                          vis_type])
    return CasTask(task_id=task.id, task_status=task.status)


@router.post(
    "/region",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Визуализировать значения анализа, группируя по всем регионам клиентов. (для analysis_sentiments region)",
    summary="Visualize analysis values by grouping by regions"
)
async def visualize_analysis_value_by_groupings_by_regions(data: list[GroupRegionallyAllCustomerAnalysis],
                                                           vis_type: VisualizationType,
                                                           title: Annotated[str, Query(
                                                               description="Заголовок визаулизации аналитики",
                                                               min_length=3,
                                                               max_length=100)] = "Customer Analysis",
                                                           title_object_count: Annotated[str, Query(
                                                                description="Обозначение количества объектов анализа отзывы / комментарии",
                                                                min_length=3,
                                                                max_length=50)] = "Count reviews",
                                                           title_analysis_value: Annotated[str, Query(
                                                                description="Обозначение значения анализа настроение / схожесть / т.п.",
                                                                min_length=3,
                                                                max_length=50)] = "Analysis value",
                                                           ):
    task = cas_api_worker.send_task(WorkerTasks.visualizer_maps_visualize_analysis_value,
                                    args=[[dict(item) for item in data], title, title_object_count, title_analysis_value,
                                          vis_type])
    return CasTask(task_id=task.id, task_status=task.status)
