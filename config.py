from enum import StrEnum
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Customer Analysis Service"
    WORKER_NAME: str = "cas_worker"
    API_V1_STR: str = "/api/v1"
    CAS_API_MAIN_KEY: str = "f0a3e8d7c6b5a4929190a1b2c3d4e5f6f7f8f9fafbfcfdfeff"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "secret"
    POSTGRES_DB: str = "postgres"

    DATABASE_POOL_SIZE = 75
    DATABASE_MAX_OVERFLOW = 20

    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    REDIS_DB: str = "0"

    def get_postgres_url(self):
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def get_redis_url(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()


class WorkerTasks(StrEnum):
    _visualizer: str = f"{settings.WORKER_NAME}.visualizer"
    visualizer_group_visualize_analysis_value: str = f"{_visualizer}.group_visualize_analysis_value"
    visualizer_group_visualize_quantity: str = f"{_visualizer}.group_visualize_quantity"
    visualizer_maps_visualize_analysis_value: str = f"{_visualizer}.maps_visualize_analysis_value"
    visualizer_histogram_visualize: str = f"{_visualizer}.histogram_visualize"

    _preparer: str = f"{settings.WORKER_NAME}.preparer"
    _provider: str = f"{settings.WORKER_NAME}.provider"

    _analyser_sentiment_preparer: str = f"{_preparer}.analyser_sentiment"
    analyser_sentiment_preparer_reviewers: str = f"{_analyser_sentiment_preparer}.reviewers"
    analyser_sentiment_preparer_commentators: str = f"{_analyser_sentiment_preparer}.commentators"

    _analyser_similarity_preparer: str = f"{_preparer}.analyser_similarity"
    analyser_similarity_preparer_products: str = f"{_analyser_similarity_preparer}.products"
    analyser_similarity_preparer_customers: str = f"{_analyser_similarity_preparer}.customers"

    _analyser_interests_provider: str = f"{_provider}.analyser_interests"
    analyser_interests_reviewers: str = f"{_analyser_interests_provider}.reviewers"
    analyser_interests_commentators: str = f"{_analyser_interests_provider}.commentators"

    _analyser_sentiment_provider: str = f"{_provider}.analyser_sentiment"
    analyser_sentiment_regionally_reviewers: str = f"{_analyser_sentiment_provider}.regionally.reviewers"
    analyser_sentiment_regionally_commentators: str = f"{_analyser_sentiment_provider}.regionally.commentators"
    analyser_sentiment_category_reviewers: str = f"{_analyser_sentiment_provider}.category.reviewers"
    analyser_sentiment_category_commentators: str = f"{_analyser_sentiment_provider}.category.commentators"

    _analyser_similarity_provider: str = f"{_provider}.analyser_similarity"
    analyser_similarity_reputation_reviewers: str = f"{_analyser_similarity_provider}.reputation.reviewers"
    analyser_similarity_reputation_commentators: str = f"{_analyser_similarity_provider}.reputation.commentators"

    _pipeline: str = f"{settings.WORKER_NAME}.pipeline"
    _pipeline_shaper: str = f"{_pipeline}.shaper"
    pipeline_shaper_comprehensive_analysis: str = f"{_pipeline_shaper}.comprehensive_analysis"
    pipeline_shaper_comprehensive_visualized_analysis: str = f"{_pipeline_shaper}.comprehensive_visualized_analysis"

    products_search = f"{settings.WORKER_NAME}.products_search"
    products_data = f"{settings.WORKER_NAME}.products_data"
    category_data = f"{settings.WORKER_NAME}.category_data"
