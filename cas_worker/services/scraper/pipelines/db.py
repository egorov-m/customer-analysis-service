from typing import Callable

from scrapy import Spider, Item
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel

from config import Config
from cas_worker.db import Database
from cas_worker.db.database import create_engine, get_session_maker
from cas_worker.db.models.comment import Comment
from cas_worker.db.models.customer import Customer
from cas_worker.db.models.product import Product
from cas_worker.db.models.review import Review
from cas_worker.services.scraper.items import ReviewItem, CommentItem, CustomerItem, ProductItem


class DbPostgresBasePipline(object):
    def __init__(self, pool: Callable[[], Session]):
        self.database = None
        self.pool = pool

    @classmethod
    def from_crawler(cls, crawler):
        cas_config: Config = Config.load_config()
        engine = create_engine(url=cas_config.dbPostgres.get_url())
        pool: sessionmaker = get_session_maker(engine)
        return cls(
            pool=pool,
        )

    def open_spider(self, spider: Spider):
        session = self.pool()
        self.database = Database(session)

    def close_spider(self, spider: Spider):
        session: Session = self.database.session
        session.close()


class DbPostgresPipeline(DbPostgresBasePipline):
    def __init__(self, pool: Callable[[], Session]):
        super().__init__(pool)

    @staticmethod
    def item_to_model(item: Item, model_obj: SQLModel) -> SQLModel:
        for field in {key for key, value in item.items() if value is not None}:
            model_obj.__setattr__(field, item[field])

    def process_item(self, item: Item, spider: Spider):
        match item:
            case CommentItem():
                item: CommentItem
                if self.database.comment.get_comment(item['customer_name_id'], item['review_id'], item['reg_datetime']):
                    return item
                comment: Comment = Comment()
                DbPostgresPipeline.item_to_model(item, comment)
                self.database.comment.add_comment(comment)
            case CustomerItem():
                item: CustomerItem
                if self.database.customer.get_customer(item['name_id']):
                    return item
                customer: Customer = Customer()
                DbPostgresPipeline.item_to_model(item, customer)
                self.database.customer.add_customer(customer)
            case ProductItem():
                item: ProductItem
                if self.database.product.get_product(item['name_id']):
                    return item
                product = Product()
                DbPostgresPipeline.item_to_model(item, product)
                self.database.product.add_product(product)
            case ReviewItem():
                item: ReviewItem
                if self.database.review.get_review(item['id']):
                    return item
                review: Review = Review()
                DbPostgresPipeline.item_to_model(item, review)
                self.database.review.add_review(review)
        return item
