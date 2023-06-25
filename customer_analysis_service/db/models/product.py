from sqlmodel import SQLModel, Field


class Product(SQLModel, table=True):
    __tablename__ = "product"

    name_id: str = Field(nullable=False, primary_key=True, max_length=150)  # at the address line
    fullname: str = Field(nullable=False, max_length=200)
    description: str = Field(nullable=False, max_length=2000)
