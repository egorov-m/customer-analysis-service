from enum import IntEnum

from sqlmodel import Session

from cas_worker.db.models import Review, RegionalLocation, Product


class ProductCategory(IntEnum):
    CATEGORY_1 = 1
    CATEGORY_2 = 2
    CATEGORY_3 = 3
    CATEGORY_4 = 4


class Provider:
    """
    Data provider base class
    """

    def __init__(self, session: Session):
        self.session = session

    @classmethod
    def _get_field_category_ru(cls, category_number: ProductCategory | int):
        return getattr(Review, f'ru_category_{category_number}')

    @classmethod
    def _get_field_category_href(cls, category_number: ProductCategory | int):
        return getattr(Review, f'href_category_{category_number}')

    @classmethod
    def _get_list_category_fields(cls):
        fields = []
        # There are a total of four numbers of categories
        for i in range(1, 5):
            fields.append(cls._get_field_category_ru(i))
            fields.append(cls._get_field_category_href(i))

        return fields

    @classmethod
    def _get_list_region_fields(cls):
        return [
            RegionalLocation.country_ru,
            RegionalLocation.country_en,
            RegionalLocation.city_ru,
            RegionalLocation.city_en,
            RegionalLocation.latitude,
            RegionalLocation.longitude
        ]

    @classmethod
    def _get_list_fields_to_group(cls):
        p = cls._get_list_category_fields()
        p.append(Product.fullname)
        return p
