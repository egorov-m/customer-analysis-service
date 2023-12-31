from datetime import datetime, date
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field


class Customer(SQLModel, table=True):
    __tablename__ = "customer"

    name_id: str = Field(nullable=False, primary_key=True, max_length=150)
    reputation: int = Field(sa_column=sa.Column(sa.Integer, nullable=False))
    country_ru: str = Field(nullable=True, max_length=100)
    country_en: str = Field(nullable=True, max_length=100)
    city_ru: str = Field(nullable=True, max_length=100)
    city_en: str = Field(nullable=True, max_length=100)
    profession: str = Field(nullable=True, max_length=100)
    reg_date: date = Field(sa_column=sa.Column(sa.Date(), nullable=False))
    count_subscribers: int = Field(sa_column=sa.Column(sa.Integer, nullable=False))


class RegionalLocation(SQLModel, table=True):
    __tablename__ = "regional_location"

    id: int = Field(sa_column=sa.Column(sa.Integer, primary_key=True, autoincrement=True))
    country_ru: str = Field(nullable=True, max_length=100)
    country_en: str = Field(nullable=True, max_length=100)
    city_ru: str = Field(nullable=True, max_length=100)
    city_en: str = Field(nullable=True, max_length=100)
    latitude: float = Field(sa_column=sa.Column(sa.Float, nullable=False))
    longitude: float = Field(sa_column=sa.Column(sa.Float, nullable=False))


class CustomerSimilarityAnalysis(SQLModel, table=True):
    __tablename__ = "customer_similarity_analysis"

    id: UUID = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        )
    )
    customer_name_id: str = Field(nullable=False, max_length=100, foreign_key="customer.name_id")
    version_mark: str = Field(nullable=False, max_length=5)
    similarity_reviews_value: float = Field(sa_column=sa.Column(sa.Float, nullable=True))
    similarity_comments_value: float = Field(sa_column=sa.Column(sa.Float, nullable=True))
    datetime_formation: datetime = Field(
        sa_column=sa.Column(
            sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()
        )
    )
