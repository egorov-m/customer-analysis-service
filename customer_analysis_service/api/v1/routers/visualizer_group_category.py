from http import HTTPStatus

from fastapi import APIRouter
from starlette import status
from starlette.responses import HTMLResponse, StreamingResponse, Response

from customer_analysis_service.api.v1.exceptions.cas_api_error import CasError, CasErrorCode
from customer_analysis_service.api.v1.schemas.analysis import CustomersForAllCategoriesBaseAnalysis
from customer_analysis_service.api.v1.schemas.visualizer import VisualizationType
from customer_analysis_service.services.visualizer.category_group import Visualizer

router = APIRouter()


@router.post(
    "/quantity",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    description="Визуализировать количество, группируя по всем категориям.",
    summary="Visualize quantities by grouping by category"
)
def visualize_quantity_by_groupings_by_category(data: list[CustomersForAllCategoriesBaseAnalysis],
                                                vis_type: VisualizationType):
    fig = Visualizer.get_fig_group_treemap(data)
    if vis_type == VisualizationType.image:
        stream = Visualizer.fig_to_image(fig)
        return StreamingResponse(stream, media_type="image/png")
    elif vis_type == VisualizationType.html:
        return HTMLResponse(content=Visualizer.fig_to_html(fig))
    else:
        raise CasError(message=f"Visualization type {vis_type} is not available",
                       error_code=CasErrorCode.VISUALIZATION_TYPE_ERROR,
                       http_status_code=HTTPStatus.BAD_REQUEST)
