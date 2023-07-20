from pydantic import BaseModel


class VisualizerSettings(BaseModel):
    root_color: str = "lightgrey"


visualizer_settings = VisualizerSettings()
