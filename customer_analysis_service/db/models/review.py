from datetime import datetime, date
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field


class Review(SQLModel, table=True):
    __tablename__ = "review"

    id: str = Field(sa_column=sa.Column(sa.Integer, primary_key=True, nullable=False))  # at the address line

    # is displayed above the title (1, etc. from left to right)
    ru_category_1: str = Field(nullable=False, max_length=150)
    ru_category_2: str = Field(nullable=False, max_length=150)
    ru_category_3: str = Field(nullable=True, max_length=150)
    ru_category_4: str = Field(nullable=True, max_length=150)

    href_category_1: str = Field(nullable=False, max_length=250)
    href_category_2: str = Field(nullable=False, max_length=250)
    href_category_3: str = Field(nullable=True, max_length=250)
    href_category_4: str = Field(nullable=True, max_length=250)

    evaluated_product_name_id: str = Field(nullable=False, max_length=250)
    customer_name_id: str = Field(nullable=False, max_length=150)
    count_user_recommend_review: int = Field(sa_column=sa.Column(sa.Integer, nullable=False))
    count_comments_review: int = Field(sa_column=sa.Column(sa.Integer, nullable=False))
    date_review: date = Field(sa_column=sa.Column(sa.Date(), nullable=False))
    advantages: str = Field(nullable=True, max_length=300)
    disadvantages: str = Field(nullable=True, max_length=300)
    text_review: str = Field(nullable=True, max_length=30000)
    general_impression: str = Field(nullable=True, max_length=300)
    star_rating: float = Field(sa_column=sa.Column(sa.Float, nullable=False))
    recommend_friends: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False))

    is_all_commenting_customers_available: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False, default=False))


class ReviewSentimentAnalysis(SQLModel, table=True):
    __tablename__ = "review_sentiment_analysis"

    id: UUID = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        )
    )
    version_mark: str = Field(nullable=False, max_length=5)
    datetime_formation: datetime = Field(
        sa_column=sa.Column(
            sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()
        )
    )
    review_id: str = Field(sa_column=sa.Column(sa.Integer, nullable=False), foreign_key="review.id")
    sentiment_value: float = Field(sa_column=sa.Column(sa.Float, nullable=False))
