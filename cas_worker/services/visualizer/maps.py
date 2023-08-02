from pandas import DataFrame
from plotly.express import scatter_mapbox
from plotly.graph_objs import Figure

from cas_shared.schemas.analysis import CustomersForAllCategoriesAnalysis
from cas_worker.services.visualizer.visualizer import Visualizer


class MapsVisualizer(Visualizer):
    def visualize_analysis_value(self,
                                 data: list[CustomersForAllCategoriesAnalysis],
                                 title_fig: str,
                                 title_quantity: str,
                                 title_analysis_value: str) -> Figure:
        df = DataFrame([item.dict() for item in data])

        df["country_ru"].fillna('—')
        df['city_ru'].fillna('—')
        df['country_en'].fillna('—')
        df['city_en'].fillna('—')
        df["region"] = df.apply(lambda x: "%s, %s | %s, %s" % (x["country_ru"],
                                                               x["city_ru"],
                                                               x["country_en"],
                                                               x["city_en"]), axis=1)
        df["point_size"] = df.apply(lambda x: int(x["object_count"]) + 50, axis=1)
        df = df.rename(columns={"analysis_value_avg": title_analysis_value, "object_count": title_quantity})

        fig = scatter_mapbox(df,
                             title=title_fig,
                             hover_name="region",
                             lat="latitude",
                             lon="longitude",
                             color=title_analysis_value,
                             color_continuous_scale="RdYlGn",
                             size="point_size",
                             zoom=1,
                             mapbox_style="carto-positron",
                             hover_data=["latitude", "longitude", title_quantity, title_analysis_value])
        fig.update_layout(
            coloraxis_colorbar=dict(
                title=title_analysis_value
            ),
            updatemenus=[
                dict(
                    buttons=Visualizer.buttons_restyle_mapbox,
                    direction="down",
                ),
            ],
        )

        return fig
