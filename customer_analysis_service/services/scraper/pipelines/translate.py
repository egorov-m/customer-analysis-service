from functools import lru_cache

from translators import translate_text
from scrapy import Item, Spider

from customer_analysis_service.services.scraper.items import CustomerItem


class TranslateCustomerGeoLocationPipeline(object):
    @staticmethod
    @lru_cache()
    def process_item(item: Item, spider: Spider):
        if isinstance(item, CustomerItem):
            item: CustomerItem
            country = item['country_ru']
            if country is not None:
                item['country_en'] = translate_text(country, to_language='en')
            city = item['city_ru']
            if city is not None:
                item['city_en'] = translate_text(city, to_language='en')

        return item
