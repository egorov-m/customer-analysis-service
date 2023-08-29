from celery import Task, chain, group
from celery.result import GroupResult

from cas_shared.schemas.task import CasPipelineComponent
from cas_shared.schemas.visualizer import VisualizationType, AnalysisVisualizationType
from cas_worker.tasks.provider.base import Provider
from cas_worker.tasks.provider.interests import InterestsAnalysisReviewersProvider, \
    InterestsAnalysisCommentatorsProvider
from cas_worker.tasks.provider.sentiment import SentimentAnalysisCategoryReviewersProvider, \
    SentimentAnalysisCategoryCommentatorsProvider, SentimentAnalysisRegionallyReviewersProvider, \
    SentimentAnalysisRegionallyCommentatorsProvider
from cas_worker.tasks.provider.similarity import SimilarityAnalysisReputationReviewersProvider, \
    SimilarityAnalysisReputationCommentatorsProvider
from cas_worker.tasks.visualizer.base import Visualizer
from cas_worker.tasks.visualizer.group import GroupVisualizerQuantity, GroupVisualizerAnalysisValue
from cas_worker.tasks.visualizer.histogram import HistogramVisualizerQuantity
from cas_worker.tasks.visualizer.maps import MapsVisualizerAnalysisValue
from config import WorkerTasks


class ComprehensiveVisualizedAnalysis(Task):
    def __init__(self):
        super().__init__()
        self.name = self.name = WorkerTasks.pipeline_shaper_comprehensive_visualized_analysis

    def run(self,
            product_name_id: str,
            analysis_vis_type: AnalysisVisualizationType,
            ia_r_title_fig: str,
            ia_r_title_quantity: str,
            ia_c_title_fig: str,
            ia_c_title_quantity: str,

            sea_c_r_title_fig: str,
            sea_c_r_title_quantity: str,
            sea_c_r_title_analysis_value: str,
            sea_c_c_title_fig: str,
            sea_c_c_title_quantity: str,
            sea_c_c_title_analysis_value: str,

            sea_r_r_title_fig: str,
            sea_r_r_title_quantity: str,
            sea_r_r_title_analysis_value: str,
            sea_r_c_title_fig: str,
            sea_r_c_title_quantity: str,
            sea_r_c_title_analysis_value: str,

            sim_reg_r_title_fig: str,
            sim_reg_c_title_fig: str,
            sim_reg_r_title_quantity: str,
            sim_reg_c_title_quantity: str,
            sim_reg_r_title_analysis_value: str,
            sim_reg_c_title_analysis_value: str,

            visualization_image_title: str,
            visualization_html_title: str
            ):
        """

        :param product_name_id:
        :param analysis_vis_type:

        analysis_type | who | what
        :param ia_r_title_fig:
        :param ia_c_title_fig:
        :param ia_r_title_quantity:
        :param ia_c_title_quantity:

        analysis_type | peculiarity | who | what
        :param sea_c_r_title_fig:
        :param sea_c_c_title_fig:
        :param sea_c_r_title_quantity:
        :param sea_c_c_title_quantity:
        :param sea_c_r_title_analysis_value:
        :param sea_c_c_title_analysis_value:
        :param sea_r_r_title_fig:
        :param sea_r_c_title_fig:
        :param sea_r_r_title_quantity:
        :param sea_r_c_title_quantity:
        :param sea_r_r_title_analysis_value:
        :param sea_r_c_title_analysis_value:

        analysis_type | peculiarity | who | what
        :param sim_reg_r_title_fig:
        :param sim_reg_c_title_fig:
        :param sim_reg_r_title_quantity:
        :param sim_reg_c_title_quantity:
        :param sim_reg_r_title_analysis_value:
        :param sim_reg_c_title_analysis_value:

        :param visualization_html_title:
        :param visualization_image_title:
        :return:
        """
        interest_analysis_reviewers_workflow = self.get_chain_analysis_tasks(
            analysis_provider_type=InterestsAnalysisReviewersProvider,
            product_name_id=product_name_id,
            analysis_vis_type=analysis_vis_type,
            vis_task_type=GroupVisualizerQuantity,
            title_fig=ia_r_title_fig,
            title_quantity=ia_r_title_quantity
        )
        interest_analysis_commentators_workflow = self.get_chain_analysis_tasks(
            analysis_provider_type=InterestsAnalysisCommentatorsProvider,
            product_name_id=product_name_id,
            analysis_vis_type=analysis_vis_type,
            vis_task_type=GroupVisualizerQuantity,
            title_fig=ia_c_title_fig,
            title_quantity=ia_c_title_quantity
        )
        sentiment_analysis_category_reviewers_workflow = self.get_chain_analysis_tasks(
            analysis_provider_type=SentimentAnalysisCategoryReviewersProvider,
            product_name_id=product_name_id,
            analysis_vis_type=analysis_vis_type,
            vis_task_type=GroupVisualizerAnalysisValue,
            title_fig=sea_c_r_title_fig,
            title_quantity=sea_c_r_title_quantity,
            title_analysis_value=sea_c_r_title_analysis_value
        )
        sentiment_analysis_category_commentators_workflow = self.get_chain_analysis_tasks(
            analysis_provider_type=SentimentAnalysisCategoryCommentatorsProvider,
            product_name_id=product_name_id,
            analysis_vis_type=analysis_vis_type,
            vis_task_type=GroupVisualizerAnalysisValue,
            title_fig=sea_c_c_title_fig,
            title_quantity=sea_c_c_title_quantity,
            title_analysis_value=sea_c_c_title_analysis_value
        )
        sentiment_analysis_regionally_reviewers_workflow = self.get_chain_analysis_tasks(
            analysis_provider_type=SentimentAnalysisRegionallyReviewersProvider,
            product_name_id=product_name_id,
            analysis_vis_type=analysis_vis_type,
            vis_task_type=MapsVisualizerAnalysisValue,
            title_fig=sea_r_r_title_fig,
            title_quantity=sea_r_r_title_quantity,
            title_analysis_value=sea_r_r_title_analysis_value
        )
        sentiment_analysis_regionally_commentators_workflow = self.get_chain_analysis_tasks(
            analysis_provider_type=SentimentAnalysisRegionallyCommentatorsProvider,
            product_name_id=product_name_id,
            analysis_vis_type=analysis_vis_type,
            vis_task_type=MapsVisualizerAnalysisValue,
            title_fig=sea_r_c_title_fig,
            title_quantity=sea_r_c_title_quantity,
            title_analysis_value=sea_r_c_title_analysis_value
        )
        similarity_analysis_by_reputation_reviewers_workflow = self.get_chain_analysis_tasks(
            analysis_provider_type=SimilarityAnalysisReputationReviewersProvider,
            product_name_id=product_name_id,
            analysis_vis_type=analysis_vis_type,
            vis_task_type=HistogramVisualizerQuantity,
            title_fig=sim_reg_r_title_fig,
            title_quantity=sim_reg_r_title_quantity,
            title_analysis_value=sim_reg_r_title_analysis_value
        )
        similarity_analysis_by_reputation_commentators_workflow = self.get_chain_analysis_tasks(
            analysis_provider_type=SimilarityAnalysisReputationCommentatorsProvider,
            product_name_id=product_name_id,
            analysis_vis_type=analysis_vis_type,
            vis_task_type=HistogramVisualizerQuantity,
            title_fig=sim_reg_c_title_fig,
            title_quantity=sim_reg_c_title_quantity,
            title_analysis_value=sim_reg_c_title_analysis_value
        )

        main_workflow = group(interest_analysis_reviewers_workflow,
                              interest_analysis_commentators_workflow,

                              sentiment_analysis_category_reviewers_workflow,
                              sentiment_analysis_category_commentators_workflow,

                              sentiment_analysis_regionally_reviewers_workflow,
                              sentiment_analysis_regionally_commentators_workflow,

                              similarity_analysis_by_reputation_reviewers_workflow,
                              similarity_analysis_by_reputation_commentators_workflow)

        result: GroupResult = main_workflow()

        return self.result_formation(group_result=result,
                                     visualization_image_title=visualization_image_title,
                                     visualization_html_title=visualization_html_title,
                                     pipeline_components_info=[ia_r_title_fig,
                                                               ia_c_title_fig,
                                                               sea_c_r_title_fig,
                                                               sea_c_c_title_fig,
                                                               sea_r_r_title_fig,
                                                               sea_r_c_title_fig,
                                                               sim_reg_r_title_fig,
                                                               sim_reg_c_title_fig])

    @staticmethod
    def result_formation(group_result: GroupResult,
                         visualization_image_title: str,
                         visualization_html_title: str,
                         pipeline_components_info: list[str]):
        result: list[CasPipelineComponent] = []
        for index, res in enumerate(group_result.children):
            c = res.children
            visualization_image_task_id = c.__getitem__(0) if c is not None else None
            visualization_image_task_id = visualization_image_task_id.id if visualization_image_task_id is not None else None
            visualization_html_task_id = c.__getitem__(1) if c is not None else None
            visualization_html_task_id = visualization_html_task_id.id if visualization_html_task_id is not None else None
            result.append(
                CasPipelineComponent(
                    analysis_task_id=res.parent.id,
                    analysis_title=pipeline_components_info[index],
                    visualization_image_task_id=visualization_image_task_id,
                    visualization_image_title=visualization_image_title,
                    visualization_html_task_id=visualization_html_task_id,
                    visualization_html_title=visualization_html_title
                )
            )

        return result

    @classmethod
    def get_chain_analysis_tasks(cls,
                                 analysis_provider_type: type[Provider],
                                 product_name_id: str,
                                 analysis_vis_type: AnalysisVisualizationType,
                                 vis_task_type: type[Visualizer],
                                 **kwargs):
        return chain(
            analysis_provider_type().s(product_name_id),
            # analysis data are transferred to visualization
            group(
                *cls.get_vis_tasks_signatures(analysis_vis_type=analysis_vis_type,
                                              vis_task_type=vis_task_type,
                                              **kwargs)
            )
        )

    @staticmethod
    def get_vis_tasks_signatures(analysis_vis_type: AnalysisVisualizationType,
                                 vis_task_type: type[Visualizer],
                                 **kwargs):
        match analysis_vis_type:
            case AnalysisVisualizationType.html:
                return [vis_task_type().s(vis_type=VisualizationType.html, **kwargs)]
            case AnalysisVisualizationType.image:
                return [vis_task_type().s(vis_type=VisualizationType.image, **kwargs)]
            case AnalysisVisualizationType.all:
                return [vis_task_type().s(vis_type=VisualizationType.image, **kwargs),
                        vis_task_type().s(vis_type=VisualizationType.html, **kwargs)]
            case AnalysisVisualizationType.none:
                return []
