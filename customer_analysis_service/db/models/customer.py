from datetime import datetime, date
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field


class Customer(SQLModel, table=True):
    __tablename__ = "customer"

    name_id: str = Field(nullable=False, primary_key=True, max_length=100)
    reputation: int = Field(sa_column=sa.Column(sa.Integer, nullable=False))
    country_ru: str = Field(nullable=True, max_length=100)
    country_en: str = Field(nullable=True, max_length=100)
    city_ru: str = Field(nullable=True, max_length=100)
    city_en: str = Field(nullable=True, max_length=100)
    profession: str = Field(nullable=True, max_length=100)
    reg_date: date = Field(sa_column=sa.Column(sa.Date(), nullable=False))
    count_subscribers: int = Field(sa_column=sa.Column(sa.Integer, nullable=False))
    # last_activity_datetime: datetime = Field(sa_column=sa.Column(sa.DateTime(), nullable=False))

    # are needed to quickly determine that the rest of the data is loaded into the database
    is_all_comments_available: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False, default=False))
    is_all_reviews_available: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False, default=False))


class CustomerGeneralAnalysis(SQLModel, table=True):
    __tablename__ = "customer_general_analysis"

    id: UUID = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        )
    )
    customer_name_id: str = Field(nullable=False, max_length=100, foreign_key="customer.name_id")
    version_mark: str = Field(nullable=False, max_length=5)
    datetime_formation: datetime = Field(
        sa_column=sa.Column(
            sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()
        )
    )
    count_all_comments: int = Field(sa_column=sa.Column(sa.Integer, nullable=False))
    count_all_reviews: int = Field(sa_column=sa.Column(sa.Integer, nullable=False))

    sentiment_all_comments_analysis_positive: float = Field(sa_column=sa.Column(sa.Float, nullable=True))
    sentiment_all_comments_analysis_negative: float = Field(sa_column=sa.Column(sa.Float, nullable=True))
    sentiment_all_comments_analysis_neutral: float = Field(sa_column=sa.Column(sa.Float, nullable=True))
    sentiment_all_comments_analysis_skip: float = Field(sa_column=sa.Column(sa.Float, nullable=True))
    sentiment_all_comments_analysis_speech: float = Field(sa_column=sa.Column(sa.Float, nullable=True))

    sentiment_all_reviews_analysis_positive: float = Field(sa_column=sa.Column(sa.Float, nullable=True))
    sentiment_all_reviews_analysis_negative: float = Field(sa_column=sa.Column(sa.Float, nullable=True))
    sentiment_all_reviews_analysis_neutral: float = Field(sa_column=sa.Column(sa.Float, nullable=True))
    sentiment_all_reviews_analysis_skip: float = Field(sa_column=sa.Column(sa.Float, nullable=True))
    sentiment_all_reviews_analysis_speech: float = Field(sa_column=sa.Column(sa.Float, nullable=True))

    similarity_analysis_all_comments: float = Field(sa_column=sa.Column(sa.Float, nullable=True))
    similarity_analysis_all_reviews: float = Field(sa_column=sa.Column(sa.Float, nullable=True))
