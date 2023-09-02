from celery import Celery

from cas_worker.pipelines.shaper import ComprehensiveVisualizedAnalysis
from cas_worker.tasks.analysis_preparer.sentiment import (
    SentimentAnalysisReviewsPreparer,
    SentimentAnalysisCommentsPreparer
)
from cas_worker.tasks.analysis_preparer.similarity import (
    SimilarityAnalysisProductsPreparer,
    SimilarityAnalysisCustomersPreparer
)
from cas_worker.tasks.analysis_provider.interests import (
    InterestsAnalysisReviewersProvider,
    InterestsAnalysisCommentatorsProvider
)
from cas_worker.tasks.analysis_provider.sentiment import (
    SentimentAnalysisCategoryReviewersProvider,
    SentimentAnalysisCategoryCommentatorsProvider,
    SentimentAnalysisRegionallyReviewersProvider,
    SentimentAnalysisRegionallyCommentatorsProvider
)
from cas_worker.tasks.analysis_provider.similarity import (
    SimilarityAnalysisReputationReviewersProvider,
    SimilarityAnalysisReputationCommentatorsProvider,
    SimilarityAnalysisCategoryReviewersProvider,
    SimilarityAnalysisCategoryCommentatorsProvider
)
from cas_worker.tasks.scraper_preparer.tasks.category_data import CategoryDataScraperTask
from cas_worker.tasks.scraper_preparer.tasks.products_data import ProductsDataScraperTask
from cas_worker.tasks.scraper_preparer.tasks.products_search import ProductsSearchScraperTask
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
cas_worker.register_task(SimilarityAnalysisCategoryReviewersProvider)
cas_worker.register_task(SimilarityAnalysisCategoryCommentatorsProvider)

cas_worker.register_task(SentimentAnalysisReviewsPreparer)
cas_worker.register_task(SentimentAnalysisCommentsPreparer)
cas_worker.register_task(SimilarityAnalysisProductsPreparer)
cas_worker.register_task(SimilarityAnalysisCustomersPreparer)

cas_worker.register_task(GroupVisualizerQuantity)
cas_worker.register_task(GroupVisualizerAnalysisValue)
cas_worker.register_task(HistogramVisualizerQuantity)
cas_worker.register_task(MapsVisualizerAnalysisValue)

cas_worker.register_task(CategoryDataScraperTask)
cas_worker.register_task(ProductsDataScraperTask)
cas_worker.register_task(ProductsSearchScraperTask)

cas_worker.register_task(ComprehensiveVisualizedAnalysis)

cas_worker.conf.timezone = "UTC"

cas_worker.conf.update(
    # task_serializer="pickle",
    result_serializer="pickle",
    accept_content=["json", "pickle"]
)
