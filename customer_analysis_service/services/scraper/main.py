import logging as log

from scrapy import Spider, Item
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet.defer import Deferred

from customer_analysis_service.db.database import Database
from customer_analysis_service.services.scraper.items import ProductItem
from customer_analysis_service.services.scraper.spiders.product import ProductSpider
from customer_analysis_service.services.scraper.spiders.customer import CustomerSpider
from customer_analysis_service.services.scraper.spiders.review import ReviewsCustomerSpider
from customer_analysis_service.services.scraper.spiders.comment import CommentsCustomerSpider


items = []


class ItemCollectorPipeline(object):
    def __init__(self):
        self.seen = set()

    @staticmethod
    def process_item(item: Item, spider: Spider):
        items.append(item)
        return item


class ScraperService:
    logger = log.getLogger('scraper_service_logger')

    def __init__(self, database: Database, crawler_process: CrawlerProcess | None = None):
        self.crawler_process: CrawlerProcess = crawler_process or CrawlerProcess(get_project_settings())
        self.database = database

    def get_products_from_search_page(self, search_input: str) -> list[ProductItem]:
        href_search_path: str = f'/?search_text={search_input}'
        self.logger.info('The search for products by search query begins!')
        deferred: Deferred = self.crawler_process.crawl(ProductSpider, href_product_path=href_search_path)
        found_items = []
        deferred.addCallback(lambda _: self.move_items(found_items))
        self.crawler_process.start()
        self.logger.info('Products found!')
        items.clear()
        return found_items

    @classmethod
    def move_items(cls, found_items: list[Item]):
        for item in items:
            found_items.append(item)
        items.clear()

        return found_items

    def start_scraping_for_product(self, product_name_id: str):
        self.logger.info(f'The parsing of the product has started: {product_name_id}!')
        deferred_customers: Deferred = self.crawler_process.crawl(CustomerSpider, product_name_ids=[product_name_id])
        found_items = []
        deferred_reviews: Deferred = deferred_customers.addCallback(
            lambda _: self.crawler_process.crawl(ReviewsCustomerSpider, customer_name_ids={item['name_id'] for item in self.move_items(found_items)}))

        deferred_comments: Deferred = deferred_reviews.addCallback(
            lambda _: self.crawler_process.crawl(CommentsCustomerSpider, customer_name_ids={item['name_id'] for item in found_items}))

        deferred_comments.addCallback(lambda _: self._set_state_data_readiness())

        self.crawler_process.start()
        self.logger.info(f'Product parsing: {product_name_id} completed!')
        items.clear()

    def start_scraping_for_category(self, href_product_path: str):
        self.logger.info(f'Starting scraping for a category: {href_product_path}')
        deferred_products: Deferred = self.crawler_process.crawl(ProductSpider, href_product_path=href_product_path)
        found_items = []
        deferred_customers: Deferred = deferred_products.addCallback(
            lambda _: self.crawler_process.crawl(CustomerSpider, product_name_ids={item['name_id'] for item in self.move_items(found_items)}))

        deferred_reviews: Deferred = deferred_customers.addCallback(
            lambda _: self.crawler_process.crawl(ReviewsCustomerSpider, customer_name_ids={item['name_id'] for item in self.move_items(found_items)}))

        deferred_comments: Deferred = deferred_reviews.addCallback(
            lambda _: self.crawler_process.crawl(CommentsCustomerSpider, customer_name_ids={item['name_id'] for item in found_items}))

        deferred_comments.addCallback(lambda _: self._set_state_data_readiness())

        self.crawler_process.start()
        self.logger.info(f'Category parsing: {href_product_path} completed!')
        items.clear()

    def _set_state_data_readiness(self):
        self.logger.info('Starting check state data!')
        for customer in self.database.customer.get_all_customers():
            self.database.customer.update_state_all_comments_available(customer, True)
            self.database.customer.update_state_all_reviews_available(customer, True)
        for product in self.database.product.get_all_products():
            self.database.product.update_state_all_customers_information_available_for_product(product, True)
        for review in self.database.review.get_all_reviews():
            self.database.review.update_state_all_commenting_customers_available(review, True)
        self.logger.info('Scraping check state data completed!')
