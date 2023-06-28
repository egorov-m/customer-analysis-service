from datetime import datetime, date

import sqlalchemy as sa
from sqlmodel import SQLModel, Field


class Customer(SQLModel, table=True):
    __tablename__ = "customer"

    name_id: str = Field(nullable=False, primary_key=True, max_length=100)
    reputation: int = Field(sa_column=sa.Column(sa.Integer, nullable=False))
    ru_country: str = Field(nullable=True, max_length=100)
    en_country: str = Field(nullable=True, max_length=100)
    ru_city: str = Field(nullable=True, max_length=100)
    en_city: str = Field(nullable=True, max_length=100)
    profession: str = Field(nullable=True, max_length=100)
    reg_date: date = Field(sa_column=sa.Column(sa.Date(), nullable=False))
    count_subscribers: int = Field(sa_column=sa.Column(sa.Integer, nullable=False))
    # last_activity_datetime: datetime = Field(sa_column=sa.Column(sa.DateTime(), nullable=False))
