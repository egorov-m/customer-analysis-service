import sqlalchemy as sa
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
