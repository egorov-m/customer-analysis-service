import os
import urllib.parse
import urllib.request
from io import BytesIO

import plotly
from pandas import DataFrame
from plotly.io import kaleido
from plotly.express import treemap
from plotly.graph_objs import Figure

from customer_analysis_service.api.v1.schemas.analysis import CustomersForAllCategoriesBaseAnalysis
from customer_analysis_service.services.visualizer.config import visualizer_settings

# Configuring plotlyjs to run the engine standalone without invoking cdn
kaleido.scope.plotlyjs = urllib.parse.urljoin('file:',
                                              urllib.request.pathname2url(os.path.join(plotly.__path__[0],
                                                                                       'package_data',
                                                                                       'plotly.min.js')))


class Visualizer:

    @staticmethod
    def get_fig_group_treemap(data: list[CustomersForAllCategoriesBaseAnalysis],
                              height: int | None = None,
                              width: int | None = None) -> Figure:
        df = DataFrame([item.dict() for item in data])
        fig = treemap(df,
                      values="customers_count",
                      path=[
                          "ru_category_1",
                          "ru_category_2",
                          "ru_category_3",
                          "ru_category_4",
                          "product_fullname"
                      ])
        fig.update_traces(root_color=visualizer_settings.root_color)
        if height is not None:
            if width is not None:
                fig.update_layout(height=height, width=width)
            else:
                fig.update_layout(height=height)

        return fig

    @staticmethod
    def fig_to_html(fig: Figure) -> str:
        return fig.to_html()

    @staticmethod
    def fig_to_image(fig: Figure) -> BytesIO:
        return BytesIO(fig.to_image(format="png", engine="kaleido"))
