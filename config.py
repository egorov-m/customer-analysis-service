from enum import StrEnum
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Customer Analysis Service"
    WORKER_NAME: str = "cas_worker"
    API_V1_STR: str = "/api/v1"

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

    _analyser_interests: str = f"{settings.WORKER_NAME}.analyser.interests"
    analyser_interests_reviewers: str = f"{_analyser_interests}.reviewers"
    analyser_interests_commentators: str = f"{_analyser_interests}.commentators"

    _analyser_sentiment: str = f"{settings.WORKER_NAME}.analyser.sentiment"
    analyser_sentiment_regionally_reviewers: str = f"{_analyser_sentiment}.regionally.reviewers"
    analyser_sentiment_regionally_commentators: str = f"{_analyser_sentiment}.regionally.commentators"
    analyser_sentiment_category_reviewers: str = f"{_analyser_sentiment}.category.reviewers"
    analyser_sentiment_category_commentators: str = f"{_analyser_sentiment}.category.commentators"

    _analyser_similarity: str = f"{settings.WORKER_NAME}.analyser.similarity"
    analyser_similarity_reputation_reviewers: str = f"{_analyser_similarity}.reputation.reviewers"
    analyser_similarity_reputation_commentators: str = f"{_analyser_similarity}.reputation.commentators"
