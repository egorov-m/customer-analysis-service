from functools import wraps
from http import HTTPStatus
from io import BytesIO

from plotly.graph_objs import Figure

from cas_shared.exceptions.cas_api_error import CasError, CasErrorCode
from cas_shared.schemas.visualizer import VisualizationType


def fig_to_html(fig: Figure) -> str:
    return fig.to_html(full_html=False)


def fig_to_image(fig: Figure,
                 img_format: str = "png",
                 height: int | None = None,
                 width: int | None = None) -> BytesIO:
    return BytesIO(fig.to_image(format=img_format,
                                engine="kaleido",
                                height=height,
                                width=width))


def menage_visualize_type():
    def decorator(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            vis_type, fig = f(*args, **kwargs)

            if vis_type == VisualizationType.image:
                stream = fig_to_image(fig)
                return stream
            elif vis_type == VisualizationType.html:
                return fig_to_html(fig)
            else:
                raise CasError(message=f"Visualization type {vis_type} is not available",
                               error_code=CasErrorCode.VISUALIZATION_TYPE_ERROR,
                               http_status_code=HTTPStatus.BAD_REQUEST)

        return wrapped_f

    return decorator
