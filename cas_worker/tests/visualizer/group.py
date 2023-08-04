from pandas import DataFrame
from plotly.express import treemap
from plotly.graph_objs import Figure

from cas_shared.schemas.analysis import CustomersForAllCategoriesAnalysis, \
    CustomersForAllCategoriesBaseAnalysis
from cas_shared.schemas.visualizer import VisualizationType
from cas_worker.tests.visualizer.config import visualizer_settings
from cas_worker.tests.visualizer.utils import menage_visualize_type
from cas_worker.tests.visualizer.visualizer import Visualizer
from config import WorkerTasks


class GroupVisualizerAnalysisValue(Visualizer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = WorkerTasks.visualizer_group_visualize_analysis_value

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


class GroupVisualizerQuantity(Visualizer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.name = WorkerTasks.visualizer_group_visualize_quantity

    def visualize_analysis_value(self,
                                 data: list[CustomersForAllCategoriesAnalysis],
                                 title_fig: str,
                                 title_quantity: str,
                                 title_analysis_value: str) -> Figure:
        pass

    def visualize_quantity(self,
                           data: list[CustomersForAllCategoriesBaseAnalysis],
                           title_fig: str,
                           title_quantity: str) -> Figure:
        df = DataFrame(data)
        # [item.dict() for item in data]
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

    @menage_visualize_type()
    def run(self,
            data: list[CustomersForAllCategoriesAnalysis | dict],
            title_fig: str,
            title_quantity: str,
            vis_type: VisualizationType) -> Figure:
        return vis_type, self.visualize_quantity(data,
                                                 title_fig,
                                                 title_quantity)
