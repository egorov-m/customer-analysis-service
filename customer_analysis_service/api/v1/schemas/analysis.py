from typing import Optional, Generator

from pydantic import BaseModel, conint


class TunedModel(BaseModel):
    class Config:
        orm_mode = True


class CustomersForAllCategoriesBaseAnalysis(TunedModel):
    ru_category_1: str
    href_category_1: str
    ru_category_2: str
    href_category_2: str
    ru_category_3: Optional[str]
    href_category_3: Optional[str]
    ru_category_4: Optional[str]
    href_category_4: Optional[str]
    product_fullname: str
    customers_count: conint(ge=0)


class CustomersForAllCategoriesAnalysis(CustomersForAllCategoriesBaseAnalysis):
    analysis_value_avg: float


class GroupRegionallyAllCustomerAnalysis(TunedModel):
    country_ru: Optional[str]
    country_en: Optional[str]
    city_ru: Optional[str]
    city_en: Optional[str]
    latitude: float
    longitude: float
    object_count: conint(ge=0)
    analysis_value_avg: float


def data_to_schema(data: list[tuple], schema: TunedModel.__class__) -> Generator[TunedModel, None, None]:
    schema_fields = schema.__fields__

    for item in data:
        schema_obj = schema.parse_obj({field: item[index] for index, field in enumerate(schema_fields)})
        yield schema_obj
