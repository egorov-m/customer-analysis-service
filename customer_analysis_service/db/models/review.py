from datetime import date

import sqlalchemy as sa
from sqlmodel import SQLModel, Field


class Review(SQLModel, table=True):
    __tablename__ = "review"

    id: str = Field(sa_column=sa.Column(sa.Integer, primary_key=True, nullable=False))  # at the address line

    # is displayed above the title (1, etc. from left to right)
    ru_category_1: str = Field(nullable=False, max_length=100)
    ru_category_2: str = Field(nullable=False, max_length=100)
    ru_category_3: str = Field(nullable=True, max_length=100)
    ru_category_4: str = Field(nullable=True, max_length=100)

    href_category_1: str = Field(nullable=False, max_length=100)
    href_category_2: str = Field(nullable=False, max_length=100)
    href_category_3: str = Field(nullable=True, max_length=100)
    href_category_4: str = Field(nullable=True, max_length=100)

    evaluated_product_name_id: str = Field(nullable=False, max_length=150, foreign_key="product.name_id")
    customer_name_id: str = Field(nullable=False, max_length=100, foreign_key="customer.name_id")
    count_user_recommend_review: int = Field(sa_column=sa.Column(sa.Integer, nullable=False))
    date_review: date = Field(sa_column=sa.Column(sa.Date(), nullable=False))
    advantages: str = Field(nullable=True, max_length=200)
    disadvantages: str = Field(nullable=True, max_length=200)
    text_review: str = Field(nullable=True, max_length=20000)
    year_service: int = Field(sa_column=sa.Column(sa.Integer, nullable=False))
    general_impression: str = Field(nullable=True, max_length=200)
    star_rating: float = Field(sa_column=sa.Column(sa.Float, nullable=False))
    recommend_friends: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False))
