from functools import wraps
from http import HTTPStatus

from starlette.responses import HTMLResponse, StreamingResponse

from cas_shared.exceptions.cas_api_error import CasError, CasErrorCode
from cas_shared.schemas.visualizer import VisualizationType
from cas_worker.services.visualizer.visualizer import Visualizer


def menage_visualize_type():
    def decorator(f):
        @wraps(f)
        async def wrapped_f(*args, **kwargs):
            vis_type, fig = await f(*args, **kwargs)

            if vis_type == VisualizationType.image:
                stream = Visualizer.fig_to_image(fig)
                return StreamingResponse(stream, media_type="image/png")
            elif vis_type == VisualizationType.html:
                return HTMLResponse(content=Visualizer.fig_to_html(fig))
            else:
                raise CasError(message=f"Visualization type {vis_type} is not available",
                               error_code=CasErrorCode.VISUALIZATION_TYPE_ERROR,
                               http_status_code=HTTPStatus.BAD_REQUEST)

        return wrapped_f

    return decorator
