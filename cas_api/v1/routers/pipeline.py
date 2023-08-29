from celery.result import AsyncResult
from fastapi import APIRouter

from cas_api.worker import cas_api_worker
from cas_shared.schemas.task import CasPipeline
from cas_shared.schemas.visualizer import AnalysisVisualizationType
from config import WorkerTasks

router = APIRouter()


@router.get(
    "/comprehensive_analysis",
    response_model=CasPipeline
)
async def comprehensive_analysis(product_name_id: str,
                                 analysis_vis_type: AnalysisVisualizationType,
                                 ia_r_title_fig: str = "Анализ интересов ревьюеров",
                                 ia_r_title_quantity: str = "Количество ревьюеров",
                                 ia_c_title_fig: str = "Анализ интересов комментаторов",
                                 ia_c_title_quantity: str = "Количество комментаторов",

                                 sea_c_r_title_fig: str = "Анализ настроений ревьюеров по категориям",
                                 sea_c_r_title_quantity: str = "Количество отзывов",
                                 sea_c_r_title_analysis_value: str = "Настроение ревьюеров",

                                 sea_c_c_title_fig: str = "Анализ настроений комментаторов по категориям",
                                 sea_c_c_title_quantity: str = "Количество комментариев",
                                 sea_c_c_title_analysis_value: str = "Настроение комментаторов",

                                 sea_r_r_title_fig: str = "Анализ настроений ревьюеров по регионам",
                                 sea_r_r_title_quantity: str = "Количество отзывов",
                                 sea_r_r_title_analysis_value: str = "Настроение ревьюеров",

                                 sea_r_c_title_fig: str = "Анализ настроений комментаторов по регионам",
                                 sea_r_c_title_quantity: str = "Количество комментариев",
                                 sea_r_c_title_analysis_value: str = "Настроение комментаторов",

                                 sim_reg_r_title_fig: str = "Анализ сходства отзывов по репутациям клиентов",
                                 sim_reg_c_title_fig: str = "Анализ сходства комментариев по репутациям клиентов",
                                 sim_reg_r_title_quantity: str = "Сходство отзывов",
                                 sim_reg_c_title_quantity: str = "Сходство комментариев",
                                 sim_reg_r_title_analysis_value: str = "Количество клиентов",
                                 sim_reg_c_title_analysis_value: str = "Количество клиентов",

                                 visualization_image_title: str = "Визуализация растрового изображения",
                                 visualization_html_title: str = "Визуализация html"):
    task: AsyncResult = cas_api_worker.send_task(WorkerTasks.pipeline_shaper_comprehensive_visualized_analysis,
                                                 args=[product_name_id,
                                                       analysis_vis_type,
                                                       ia_r_title_fig, ia_r_title_quantity, ia_c_title_fig, ia_c_title_quantity,
                                                       sea_c_r_title_fig, sea_c_r_title_quantity, sea_c_r_title_analysis_value,
                                                       sea_c_c_title_fig, sea_c_c_title_quantity, sea_c_c_title_analysis_value,
                                                       sea_r_r_title_fig, sea_r_r_title_quantity, sea_r_r_title_analysis_value,
                                                       sea_r_c_title_fig, sea_r_c_title_quantity, sea_r_c_title_analysis_value,
                                                       sim_reg_r_title_fig, sim_reg_c_title_fig, sim_reg_r_title_quantity,
                                                       sim_reg_c_title_quantity, sim_reg_r_title_analysis_value,
                                                       sim_reg_c_title_analysis_value,
                                                       visualization_image_title, visualization_html_title])
    return CasPipeline(
        pipeline_id=task.id,
        pipeline_status=task.status
    )
