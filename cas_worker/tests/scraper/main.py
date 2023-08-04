import json
import logging as log
import subprocess

from scrapy import Spider, Item
from typing import Type

from cas_worker.tests.scraper.items import ProductItem, CustomerItem
from cas_worker.tests.scraper.spiders.product import ProductSpider
from cas_worker.tests.scraper.spiders.customer import CustomerSpider
from cas_worker.tests.scraper.spiders.review import ReviewsCustomerSpider
from cas_worker.tests.scraper.spiders.comment import CommentsCustomerSpider


BUFFER_FILE_PATH: str = './.scrapy/buffer.json'


def _start_sub_process_spider(spider_cls: Type[Spider], **kwargs):
    cmd = ["scrapy", "crawl", spider_cls.name]
    for key, value in kwargs.items():
        if isinstance(value, list):
            cmd.append("-a")
            cmd.append(f"{key}={' '.join(str(x) for x in value)}")
        else:
            cmd.append("-a")
            cmd.append(f"{key}='{value}'")
    cmd.append("-o")
    cmd.append(BUFFER_FILE_PATH)

    subprocess.run(cmd)


def _extract_from_buffer() -> list[Item]:
    try:
        with open(BUFFER_FILE_PATH, 'r+', encoding='utf-8') as json_file:
            data = json_file.read()
            data = json.loads(data)
            json_file.truncate(0)
    except Exception:
        pass

    return data


class ScraperService:
    logger = log.getLogger('scraper_service_logger')

    @classmethod
    def get_products_from_search_page(cls, search_input: str, max_count_items: int = 5) -> list[ProductItem]:
        href_search_path: str = f'/?search_text={search_input}'
        cls.logger.info('The search for products by search query begins!')

        _start_sub_process_spider(ProductSpider,
                                  href_product_path=href_search_path,
                                  max_count_items=max_count_items)

        cls.logger.info('Products found!')

        return _extract_from_buffer()

    @classmethod
    def start_scraping_for_product(cls, product_name_id: str):
        cls.logger.info(f'The parsing of the product has started: {product_name_id}!')

        _start_sub_process_spider(CustomerSpider, product_name_ids=[product_name_id])

        customers: list[CustomerItem] = _extract_from_buffer()

        _start_sub_process_spider(ReviewsCustomerSpider, customer_name_ids=[item['name_id'] for item in customers])

        _start_sub_process_spider(CommentsCustomerSpider, customer_name_ids=[item['name_id'] for item in customers])

        cls.logger.info(f'Product parsing: {product_name_id} completed!')

    @classmethod
    def start_scraping_for_category(cls, href_product_path: str):
        cls.logger.info(f'Starting scraping for a category: {href_product_path}')

        _start_sub_process_spider(ProductSpider, href_product_path=href_product_path)

        products: list[ProductItem] = _extract_from_buffer()

        _start_sub_process_spider(CustomerSpider, product_name_ids=[item['name_id'] for item in products])

        customers: list[CustomerItem] = _extract_from_buffer()

        _start_sub_process_spider(ReviewsCustomerSpider, customer_name_ids=[item['name_id'] for item in customers])

        _start_sub_process_spider(CommentsCustomerSpider, customer_name_ids=[item['name_id'] for item in customers])

        cls.logger.info(f'Category parsing: {href_product_path} completed!')

    # def _set_state_data_readiness(self):
    #     self.logger.info('Starting check state data!')
    #     for customer in self.database.customer.get_all_customers():
    #         self.database.customer.update_state_all_comments_available(customer, True)
    #         self.database.customer.update_state_all_reviews_available(customer, True)
    #     for product in self.database.product.get_all_products():
    #         self.database.product.update_state_all_customers_information_available_for_product(product, True)
    #     for review in self.database.review.get_all_reviews():
    #         self.database.review.update_state_all_commenting_customers_available(review, True)
    #     self.logger.info('Scraping check state data completed!')
