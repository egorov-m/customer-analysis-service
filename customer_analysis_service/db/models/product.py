from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field


class Product(SQLModel, table=True):
    __tablename__ = "product"

    name_id: str = Field(nullable=False, primary_key=True, max_length=250)  # at the address line
    fullname: str = Field(nullable=False, max_length=250)
    image_url: str = Field(nullable=True, max_length=200)
    description: str = Field(nullable=True, max_length=5000)

    is_all_customers_information_available_for_product: bool = Field(sa_column=sa.Column(sa.Boolean,
                                                                                         nullable=False,
                                                                                         default=False))


class ProductSimilarityAnalysis(SQLModel, table=True):
    __tablename__ = "product_similarity_analysis"

    id: UUID = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        )
    )
    product_name_id: str = Field(nullable=False, max_length=250, foreign_key="product.name_id")
    version_mark: str = Field(nullable=False, max_length=5)
    similarity_reviews_value: float = Field(sa_column=sa.Column(sa.Float, nullable=True))
    similarity_comments_value: float = Field(sa_column=sa.Column(sa.Float, nullable=True))
    datetime_formation: datetime = Field(
        sa_column=sa.Column(
            sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()
        )
    )
