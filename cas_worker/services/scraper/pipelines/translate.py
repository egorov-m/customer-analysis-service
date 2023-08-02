from functools import lru_cache

from translators import translate_text
from scrapy import Item, Spider

from cas_worker.services.scraper.items import CustomerItem


class TranslateCustomerGeoLocationPipeline(object):
    @staticmethod
    def process_item(item: Item, spider: Spider):
        if isinstance(item, CustomerItem):
            item: CustomerItem
            country = item['country_ru']
            if country is not None:
                item['country_en'] = TranslateCustomerGeoLocationPipeline.translate_item_field(country)
            else:
                item['country_en'] = None
            city = item['city_ru']
            if city is not None:
                item['city_en'] = TranslateCustomerGeoLocationPipeline.translate_item_field(city)
            else:
                item['city_en'] = None

        return item

    @staticmethod
    @lru_cache()
    def translate_item_field(text: str):
        return translate_text(text, to_language='en')
