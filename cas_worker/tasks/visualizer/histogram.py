from pandas import DataFrame
from plotly.express import histogram
from plotly.graph_objs import Figure

from cas_shared.schemas.base import TunedModel
from cas_worker.tasks.visualizer.base import Visualizer
from config import WorkerTasks


class HistogramVisualizerQuantity(Visualizer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.name = WorkerTasks.visualizer_histogram_visualize

    def visualize_analysis_value(self,
                                 data: list[TunedModel | dict],
                                 title_fig: str,
                                 title_quantity: str,
                                 title_analysis_value: str) -> Figure:
        df = DataFrame(data)
        df = df.rename(columns={df.columns[1]: title_analysis_value})
        # [item.dict() for item in data]

        fig = histogram(df,
                        x=df.columns[0],
                        y=df.columns[1],
                        title=title_fig,
                        marginal="rug",
                        text_auto=True,
                        histfunc="avg")
        fig.update_layout(
            bargap=0.1
        )

        return fig
