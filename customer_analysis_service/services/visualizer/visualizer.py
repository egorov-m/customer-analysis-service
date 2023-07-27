import os
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from io import BytesIO

import plotly
from plotly.io import kaleido
from plotly.graph_objs import Figure

from customer_analysis_service.api.v1.schemas.analysis import CustomersForAllCategoriesAnalysis


# Configuring plotlyjs to run the engine standalone without invoking cdn
kaleido.scope.plotlyjs = urllib.parse.urljoin('file:',
                                              urllib.request.pathname2url(os.path.join(plotly.__path__[0],
                                                                                       'package_data',
                                                                                       'plotly.min.js')))


class Visualizer(ABC):
    buttons_restyle_category_chart: list = [
        dict(
            args=["type", "treemap"],
            label="Treemap Chart",
            method="restyle"
        ),
        dict(
            args=["type", "icicle"],
            label="Icicle Chart",
            method="restyle"
        ),
        dict(
            args=["type", "sunburst"],
            label="Sunburst Chart",
            method="restyle"
        )
    ]
    buttons_restyle_mapbox: list = [
        dict(
            args=["mapbox.style", "carto-positron"],
            label="Carto positron style",
            method="relayout"
        ),
        dict(
            args=["mapbox.style", "carto-darkmatter"],
            label="Carto darkmatter style",
            method="relayout"
        ),
        dict(
            args=["mapbox.style", "open-street-map"],
            label="Open street map style",
            method="relayout"
        ),
        dict(
            args=["mapbox.style", "stamen-terrain"],
            label="Stamen terrain style",
            method="relayout"
        ),
        dict(
            args=["mapbox.style", "stamen-toner"],
            label="Stamen toner style",
            method="relayout"
        )
    ]
    group_category_list: list = [
        "ru_category_1",
        "ru_category_2",
        "ru_category_3",
        "ru_category_4",
        "product_fullname"
    ]

    @abstractmethod
    def visualize_analysis_value(self,
                                 data: list[CustomersForAllCategoriesAnalysis],
                                 title_fig: str,
                                 title_quantity: str,
                                 title_analysis_value: str
                                 ) -> Figure:
        pass

    @staticmethod
    def fig_to_html(fig: Figure) -> str:
        return fig.to_html(full_html=False)

    @staticmethod
    def fig_to_image(fig: Figure,
                     img_format: str = "png",
                     height: int | None = None,
                     width: int | None = None) -> BytesIO:
        return BytesIO(fig.to_image(format=img_format,
                                    engine="kaleido",
                                    height=height,
                                    width=width))
