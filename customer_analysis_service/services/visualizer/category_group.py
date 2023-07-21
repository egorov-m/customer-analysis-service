import os
import urllib.parse
import urllib.request
from io import BytesIO

import plotly
from pandas import DataFrame
from plotly.io import kaleido
from plotly.express import treemap
from plotly.graph_objs import Figure

from customer_analysis_service.api.v1.schemas.analysis import CustomersForAllCategoriesBaseAnalysis, \
    CustomersForAllCategoriesAnalysis
from customer_analysis_service.services.visualizer.config import visualizer_settings

# Configuring plotlyjs to run the engine standalone without invoking cdn
kaleido.scope.plotlyjs = urllib.parse.urljoin('file:',
                                              urllib.request.pathname2url(os.path.join(plotly.__path__[0],
                                                                                       'package_data',
                                                                                       'plotly.min.js')))


class Visualizer:
    buttons: list = [
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
    group_category_list: list = [
        "ru_category_1",
        "ru_category_2",
        "ru_category_3",
        "ru_category_4",
        "product_fullname"
    ]

    @staticmethod
    def get_fig_group_quantity(data: list[CustomersForAllCategoriesBaseAnalysis],
                               title_fig: str,
                               title_quantity: str,
                               height: int | None = None,
                               width: int | None = None) -> Figure:
        df = DataFrame([item.dict() for item in data])
        df = df.fillna(" ")  # Category 3, 4 may not be available
        fig = treemap(df,
                      title=title_fig,
                      values="customers_count",
                      path=Visualizer.group_category_list)
        fig.update_traces(
            root_color=visualizer_settings.root_color,
            hovertemplate=f"<b>%{{label}} </b> <br> {title_quantity}: %{{value}}")
        if height is not None:
            if width is not None:
                fig.update_layout(height=height, width=width)
            else:
                fig.update_layout(height=height)
        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=Visualizer.buttons,
                    direction="down",
                ),
            ]
        )

        return fig

    @staticmethod
    def get_fig_group_analysis_value(data: list[CustomersForAllCategoriesAnalysis],
                                     title_fig: str,
                                     title_quantity: str,
                                     title_analysis_value: str,
                                     height: int | None = None,
                                     width: int | None = None) -> Figure:
        df = DataFrame([item.dict() for item in data])
        df = df.fillna(" ")  # Category 3, 4 may not be available
        fig = treemap(df,
                      title=title_fig,
                      values="customers_count",
                      color="analysis_value_avg",
                      color_continuous_scale="RdYlGn",
                      path=Visualizer.group_category_list)
        fig.update_traces(
            root_color=visualizer_settings.root_color,
            hovertemplate=f"<b>%{{label}} </b> <br> {title_quantity}: %{{value}}<br> {title_analysis_value}: %{{color}}")
        fig.update_layout(
            coloraxis_colorbar=dict(
                title=title_analysis_value
            ),
            updatemenus=[
                dict(
                    buttons=Visualizer.buttons,
                    direction="down",
                ),
            ],
        )
        if height is not None:
            if width is not None:
                fig.update_layout(height=height, width=width)
            else:
                fig.update_layout(height=height)

        return fig

    @staticmethod
    def fig_to_html(fig: Figure) -> str:
        return fig.to_html(full_html=False)

    @staticmethod
    def fig_to_image(fig: Figure) -> BytesIO:
        return BytesIO(fig.to_image(format="png", engine="kaleido"))
