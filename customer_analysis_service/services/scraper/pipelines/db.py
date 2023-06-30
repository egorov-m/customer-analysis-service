from itemadapter import ItemAdapter
from typing import Callable

from scrapy import Spider
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from customer_analysis_service.config import Config
from customer_analysis_service.db import Database
from customer_analysis_service.db.database import create_engine, get_session_maker
from customer_analysis_service.db.models.product import Product
from customer_analysis_service.services.scraper.items import ProductItem


class DbPostgresBasePipline(object):
    def __init__(self, pool: Callable[[], Session]):
        self.database = None
        self.pool = pool

    @classmethod
    def from_crawler(cls, crawler):
        cas_config: Config = Config.load_config()
        async_engine = create_engine(url=cas_config.dbPostgres.get_url())
        pool: sessionmaker = get_session_maker(async_engine)
        return cls(
            pool=pool,
        )

    def open_spider(self, spider: Spider):
        session = self.pool()
        self.database = Database(session)
        pass

    def close_spider(self, spider: Spider):
        session: Session = self.database.session
        session.close()


class DbPostgresProductPipeline(DbPostgresBasePipline):
    def __init__(self, pool: Callable[[], Session]):
        super().__init__(pool)

    def process_item(self, item: ProductItem, spider: Spider):
        adapter: ItemAdapter = ItemAdapter(item)

        if not self.database.product.get_product(adapter['name_id']):
            return

        product: Product = Product()
        product.name_id = adapter['name_id']
        product.fullname = adapter['fullname']
        product.image_url = adapter['image_url']
        product.description = adapter['description']
        self.database.product.add_product(product)
        return item
