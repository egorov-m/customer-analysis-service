import os
import urllib.parse
import urllib.request
from abc import ABC

import plotly
from celery import Task
from plotly.io import kaleido
from plotly.graph_objs import Figure

from cas_shared.schemas.analysis import CustomersForAllCategoriesAnalysis
from cas_shared.schemas.base import TunedModel
from cas_shared.schemas.visualizer import VisualizationType
from cas_worker.tasks.visualizer.utils import menage_visualize_type

# Configuring plotlyjs to run the engine standalone without invoking cdn
kaleido.scope.plotlyjs = urllib.parse.urljoin('file:',
                                              urllib.request.pathname2url(os.path.join(plotly.__path__[0],
                                                                                       'package_data',
                                                                                       'plotly.min.js')))


class Visualizer(ABC, Task):
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

    def visualize_analysis_value(self,
                                 data: list[TunedModel | dict],
                                 title_fig: str,
                                 title_quantity: str,
                                 title_analysis_value: str) -> Figure:
        pass

    @menage_visualize_type()
    def run(self,
            data: list[CustomersForAllCategoriesAnalysis | dict],
            title_fig: str,
            title_quantity: str,
            title_analysis_value: str,
            vis_type: VisualizationType):
        return vis_type, self.visualize_analysis_value(data,
                                                       title_fig,
                                                       title_quantity,
                                                       title_analysis_value)
