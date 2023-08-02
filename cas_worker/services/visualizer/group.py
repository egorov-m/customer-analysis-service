from pandas import DataFrame
from plotly.express import treemap
from plotly.graph_objs import Figure

from cas_shared.schemas.analysis import CustomersForAllCategoriesAnalysis, \
    CustomersForAllCategoriesBaseAnalysis
from cas_worker.services.visualizer.config import visualizer_settings
from cas_worker.services.visualizer.visualizer import Visualizer


class GroupVisualizer(Visualizer):
    def visualize_analysis_value(self,
                                 data: list[CustomersForAllCategoriesAnalysis],
                                 title_fig: str,
                                 title_quantity: str,
                                 title_analysis_value: str) -> Figure:
        df = DataFrame([item.dict() for item in data])
        df = df.fillna(" ")  # Category 3, 4 may not be available
        fig = treemap(df,
                      title=title_fig,
                      values="customers_count",
                      color="analysis_value_avg",
                      color_continuous_scale="RdYlGn",
                      path=self.group_category_list)
        fig.update_traces(
            root_color=visualizer_settings.root_color,
            hovertemplate=f"<b>%{{label}} </b> <br> {title_quantity}: %{{value}}<br> {title_analysis_value}: %{{color}}")
        fig.update_layout(
            coloraxis_colorbar=dict(
                title=title_analysis_value
            ),
            updatemenus=[
                dict(
                    buttons=self.buttons_restyle_category_chart,
                    direction="down",
                ),
            ],
        )

        return fig

    def visualize_quantity(self,
                           data: list[CustomersForAllCategoriesBaseAnalysis],
                           title_fig: str,
                           title_quantity: str) -> Figure:
        df = DataFrame([item.dict() for item in data])
        df = df.fillna(" ")  # Category 3, 4 may not be available
        fig = treemap(df,
                      title=title_fig,
                      values="customers_count",
                      path=self.group_category_list)
        fig.update_traces(
            root_color=visualizer_settings.root_color,
            hovertemplate=f"<b>%{{label}} </b> <br> {title_quantity}: %{{value}}")
        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=self.buttons_restyle_category_chart,
                    direction="down",
                ),
            ]
        )

        return fig
