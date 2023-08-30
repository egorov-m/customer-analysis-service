from pydantic import HttpUrl

from cas_shared.schemas.base import TunedModel


class FoundProduct(TunedModel):
    name_id: str
    fullname: str
    image_url: HttpUrl
