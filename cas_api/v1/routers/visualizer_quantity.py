from typing import Annotated

from fastapi import APIRouter, Query
from starlette import status

from cas_shared.schemas.analysis import CustomersForAllCategoriesBaseAnalysis
from cas_shared.schemas.task import CasTask
from cas_shared.schemas.visualizer import VisualizationType
from cas_worker.worker import cas_worker
from config import WorkerTasks

router = APIRouter()


@router.post(
    "/category",
    response_model=CasTask,
    status_code=status.HTTP_200_OK,
    description="Визуализировать количество, группируя по всем категориям. (для analysis_interests)",
    summary="Visualize quantities by grouping by category"
)
async def visualize_quantity_by_groupings_by_category(data: list[CustomersForAllCategoriesBaseAnalysis],
                                                      vis_type: VisualizationType,
                                                      title: Annotated[str, Query(
                                                          description="Заголовок визаулизации аналитики",
                                                          min_length=3,
                                                          max_length=100)] = "Customer Analysis",
                                                      title_quantity: Annotated[str, Query(
                                                          description="Обозначение количественного значения клиенты / отзывы / комментарии",
                                                          min_length=3,
                                                          max_length=50)] = "Count customers"
                                                      ):
    task = cas_worker.send_task(WorkerTasks.visualizer_group_visualize_quantity,
                                args=[[dict(item) for item in data], title, title_quantity, vis_type])
    return CasTask(task_id=task.id, task_status=task.status)
