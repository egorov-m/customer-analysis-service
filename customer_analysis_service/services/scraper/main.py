import logging as log

from scrapy import Spider, Item
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet.defer import Deferred, DeferredList
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from customer_analysis_service.config import Config
from customer_analysis_service.db.database import create_engine, get_session_maker, Database
from customer_analysis_service.services.scraper.spiders.product import ProductSpider
from customer_analysis_service.services.scraper.spiders.customer import CustomerSpider
from customer_analysis_service.services.scraper.spiders.review import ReviewsCustomerSpider
from customer_analysis_service.services.scraper.spiders.comment import CommentsCustomerSpider


logger = log.getLogger('scraping_logger')

cas_config: Config = Config.load_config()
engine = create_engine(url=cas_config.dbPostgres.get_url())
pool: sessionmaker = get_session_maker(engine)
session: Session = pool()
database = Database(session)
items = []


class ItemCollectorPipeline(object):
    def __init__(self):
        self.seen = set()

    @staticmethod
    def process_item(item: Item, spider: Spider):
        if 'name_id' in item:
            items.append(item['name_id'])
        return item


def start_scraping_for_search_products(entered_search_text: str):
    href_product_path: str = f'/?search_text={entered_search_text}'
    logger.info(f'Starting scraping for a query: {href_product_path}')
    _start_scraping_for_products(href_product_path)
    logger.info('Scraping full information about the product and its customers is completed!')


def start_scraping_for_category(href_product_path: str):
    logger.info(f'Starting scraping for a category: {href_product_path}')
    _start_scraping_for_products(href_product_path)
    logger.info('Scraping full information about the product and its customers is completed!')


def _start_scraping_for_products(href_product_path: str):
    process = CrawlerProcess(get_project_settings())
    deferred_products: Deferred = process.crawl(ProductSpider, href_product_path=href_product_path)

    deferred_customers: Deferred = deferred_products.addCallback(lambda _: process.crawl(CustomerSpider, product_name_ids=items))

    deferred_reviews: Deferred = deferred_customers.addCallback(lambda _: process.crawl(ReviewsCustomerSpider, customer_name_ids=items))

    deferred_comments: Deferred = deferred_reviews.addCallback(lambda _: process.crawl(CommentsCustomerSpider, customer_name_ids=items))

    deferred: Deferred = deferred_comments.addCallback(lambda _: _set_state_data_readiness())

    deferred_list = DeferredList([deferred_products, deferred_customers, deferred_reviews, deferred_comments, deferred])
    deferred_list.addBoth(lambda _: process.stop())

    process.start()


def _set_state_data_readiness():
    logger.info('Starting check state data!')
    for customer in database.customer.get_all_customers():
        database.customer.update_state_all_comments_available(customer, True)
        database.customer.update_state_all_reviews_available(customer, True)
    for product in database.product.get_all_products():
        database.product.update_state_all_customers_information_available_for_product(product, True)
    for review in database.review.get_all_reviews():
        database.review.update_state_all_commenting_customers_available(review, True)
    logger.info('Scraping check state data completed!')
