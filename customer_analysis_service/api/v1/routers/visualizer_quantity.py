from typing import Annotated

from fastapi import APIRouter, Response, Query
from starlette import status

from customer_analysis_service.api.v1.schemas.analysis import CustomersForAllCategoriesBaseAnalysis
from customer_analysis_service.api.v1.schemas.visualizer import VisualizationType
from customer_analysis_service.services.visualizer.group import GroupVisualizer
from customer_analysis_service.utils.api import menage_visualize_type

router = APIRouter()


@router.post(
    "/category",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    description="Визуализировать количество, группируя по всем категориям. (для analysis_interests)",
    summary="Visualize quantities by grouping by category"
)
@menage_visualize_type()
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
    visualizer: GroupVisualizer = GroupVisualizer()
    return vis_type, visualizer.visualize_quantity(data,
                                                   title_fig=title,
                                                   title_quantity=title_quantity)
