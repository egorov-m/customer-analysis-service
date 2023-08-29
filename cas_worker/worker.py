from celery import Celery

from cas_worker.pipelines.shaper import ComprehensiveVisualizedAnalysis
from cas_worker.tasks.provider.interests import InterestsAnalysisReviewersProvider,\
    InterestsAnalysisCommentatorsProvider
from cas_worker.tasks.provider.sentiment import (
    SentimentAnalysisCategoryReviewersProvider,
    SentimentAnalysisCategoryCommentatorsProvider,
    SentimentAnalysisRegionallyReviewersProvider,
    SentimentAnalysisRegionallyCommentatorsProvider
)
from cas_worker.tasks.provider.similarity import SimilarityAnalysisReputationReviewersProvider,\
    SimilarityAnalysisReputationCommentatorsProvider
from cas_worker.tasks.visualizer.group import GroupVisualizerQuantity, GroupVisualizerAnalysisValue
from cas_worker.tasks.visualizer.histogram import HistogramVisualizerQuantity
from cas_worker.tasks.visualizer.maps import MapsVisualizerAnalysisValue
from config import settings


cas_worker = Celery(
    "cas_worker",
    broker=settings.get_redis_url(),
    backend=settings.get_redis_url(),
    include=["cas_worker.tasks"]
)

cas_worker.register_task(InterestsAnalysisReviewersProvider)
cas_worker.register_task(InterestsAnalysisCommentatorsProvider)

cas_worker.register_task(SentimentAnalysisCategoryReviewersProvider)
cas_worker.register_task(SentimentAnalysisCategoryCommentatorsProvider)
cas_worker.register_task(SentimentAnalysisRegionallyReviewersProvider)
cas_worker.register_task(SentimentAnalysisRegionallyCommentatorsProvider)

cas_worker.register_task(SimilarityAnalysisReputationReviewersProvider)
cas_worker.register_task(SimilarityAnalysisReputationCommentatorsProvider)

cas_worker.register_task(GroupVisualizerQuantity)
cas_worker.register_task(GroupVisualizerAnalysisValue)
cas_worker.register_task(HistogramVisualizerQuantity)
cas_worker.register_task(MapsVisualizerAnalysisValue)

cas_worker.register_task(ComprehensiveVisualizedAnalysis)

cas_worker.conf.timezone = "UTC"

cas_worker.conf.update(
    # task_serializer="pickle",
    result_serializer="pickle",
    accept_content=["json", "pickle"]
)
