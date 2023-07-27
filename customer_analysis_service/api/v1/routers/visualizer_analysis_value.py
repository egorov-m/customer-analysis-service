from typing import Annotated

from fastapi import APIRouter, Query
from starlette import status
from starlette.responses import Response

from customer_analysis_service.api.v1.schemas.analysis import CustomersForAllCategoriesAnalysis,\
    GroupRegionallyAllCustomerAnalysis
from customer_analysis_service.api.v1.schemas.visualizer import VisualizationType
from customer_analysis_service.services.visualizer.group import GroupVisualizer
from customer_analysis_service.services.visualizer.maps import MapsVisualizer
from customer_analysis_service.utils.api import menage_visualize_type

router = APIRouter()


@router.post(
    "/category",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    description="Визуализировать значения анализа, группируя по всем категориям. (для analysis_sentiments category)",
    summary="Visualize analysis values by grouping by category"
)
@menage_visualize_type()
async def visualize_analysis_value_by_groupings_by_category(data: list[CustomersForAllCategoriesAnalysis],
                                                            vis_type: VisualizationType,
                                                            title: Annotated[str, Query(
                                                                description="Заголовок визаулизации аналитики",
                                                                min_length=3,
                                                                max_length=100)] = "Customer Analysis",
                                                            title_quantity: Annotated[str, Query(
                                                                description="Обозначение количественного значения клиенты / отзывы / комментарии",
                                                                min_length=3,
                                                                max_length=50)] = "Count customers",
                                                            title_analysis_value: Annotated[str, Query(
                                                                description="Обозначение значения анализа настроение / схожесть / т.п.",
                                                                min_length=3,
                                                                max_length=50)] = "Analysis value",
                                                            ):
    visualizer: GroupVisualizer = GroupVisualizer()
    return vis_type, visualizer.visualize_analysis_value(data,
                                                         title_fig=title,
                                                         title_quantity=title_quantity,
                                                         title_analysis_value=title_analysis_value)


@router.post(
    "/region",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    description="Визуализировать значения анализа, группируя по всем регионам клиентов. (для analysis_sentiments region)",
    summary="Visualize analysis values by grouping by regions"
)
@menage_visualize_type()
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
    visualizer: MapsVisualizer = MapsVisualizer()
    return vis_type, visualizer.visualize_analysis_value(data,
                                                         title_fig=title,
                                                         title_quantity=title_object_count,
                                                         title_analysis_value=title_analysis_value)
