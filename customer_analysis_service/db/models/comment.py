from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field


class Comment(SQLModel, table=True):
    __tablename__ = "comment"

    # id is only in our database
    id: int = Field(sa_column=sa.Column(sa.Integer, primary_key=True, autoincrement=True))

    review_id: int = Field(sa_column=sa.Column(sa.Integer, nullable=False))
    customer_name_id: str = Field(nullable=False, max_length=150)  # at the address line
    reg_datetime: datetime = Field(sa_column=sa.Column(sa.DateTime(), nullable=False))
    text_comment: str = Field(nullable=True, max_length=10000)


class CommentSentimentAnalysis(SQLModel, table=True):
    __tablename__ = "comment_sentiment_analysis"

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
    comment_id: int = Field(sa_column=sa.Column(sa.Integer, nullable=False), foreign_key="comment.id")
    sentiment_value: float = Field(sa_column=sa.Column(sa.Float, nullable=False))
