from pydantic import BaseModel
from typing import Generator


class TunedModel(BaseModel):
    class Config:
        orm_mode = True


def data_to_schema(data: list[tuple], schema: TunedModel.__class__) -> Generator[TunedModel, None, None]:
    schema_fields = schema.__fields__

    for item in data:
        schema_obj = schema.parse_obj({field: item[index] for index, field in enumerate(schema_fields)})
        yield schema_obj


def data_to_schema_dict(data: list[tuple], schema: TunedModel.__class__) -> Generator[dict, None, None]:
    schema_fields = schema.__fields__

    for item in data:
        schema_obj = {field: item[index] for index, field in enumerate(schema_fields)}
        yield schema_obj
