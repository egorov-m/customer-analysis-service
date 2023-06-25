from datetime import datetime

import sqlalchemy as sa
from sqlmodel import SQLModel, Field


class Comment(SQLModel, table=True):
    __tablename__ = "comment"

    # id is only in our database
    id: int = Field(sa_column=sa.Column(sa.Integer, primary_key=True, autoincrement=True))

    review_id: int = Field(sa_column=sa.Column(sa.Integer, foreign_key="review.id"))
    customer_name_id: str = Field(nullable=False, max_length=100, foreign_key="customer.name_id")  # at the address line
    reg_datetime: datetime = Field(sa_column=sa.Column(sa.DateTime(), nullable=False))
    text_comment: str = Field(nullable=True, max_length=10000)
