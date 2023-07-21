from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Query
from starlette import status
from starlette.responses import HTMLResponse, StreamingResponse, Response

from customer_analysis_service.api.v1.exceptions.cas_api_error import CasError, CasErrorCode
from customer_analysis_service.api.v1.schemas.analysis import CustomersForAllCategoriesBaseAnalysis, \
    CustomersForAllCategoriesAnalysis
from customer_analysis_service.api.v1.schemas.visualizer import VisualizationType
from customer_analysis_service.services.visualizer.category_group import Visualizer

router = APIRouter()


@router.post(
    "/quantity",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    description="Визуализировать количество, группируя по всем категориям. (для analysis_interests)",
    summary="Visualize quantities by grouping by category"
)
def visualize_quantity_by_groupings_by_category(data: list[CustomersForAllCategoriesBaseAnalysis],
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
    fig = Visualizer.get_fig_group_quantity(data,
                                            title_fig=title,
                                            title_quantity=title_quantity)
    if vis_type == VisualizationType.image:
        stream = Visualizer.fig_to_image(fig)
        return StreamingResponse(stream, media_type="image/png")
    elif vis_type == VisualizationType.html:
        return HTMLResponse(content=Visualizer.fig_to_html(fig))
    else:
        raise CasError(message=f"Visualization type {vis_type} is not available",
                       error_code=CasErrorCode.VISUALIZATION_TYPE_ERROR,
                       http_status_code=HTTPStatus.BAD_REQUEST)


@router.post(
    "/analysis_value",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    description="Визуализировать значения анализа, группируя по всем категориям. (для analysis_interests)",
    summary="Visualize analysis values by grouping by category"
)
def visualize_analysis_value_by_groupings_by_category(data: list[CustomersForAllCategoriesAnalysis],
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
    fig = Visualizer.get_fig_group_analysis_value(data,
                                                  title_fig=title,
                                                  title_quantity=title_quantity,
                                                  title_analysis_value=title_analysis_value)
    if vis_type == VisualizationType.image:
        stream = Visualizer.fig_to_image(fig)
        return StreamingResponse(stream, media_type="image/png")
    elif vis_type == VisualizationType.html:
        return HTMLResponse(content=Visualizer.fig_to_html(fig))
    else:
        raise CasError(message=f"Visualization type {vis_type} is not available",
                       error_code=CasErrorCode.VISUALIZATION_TYPE_ERROR,
                       http_status_code=HTTPStatus.BAD_REQUEST)
