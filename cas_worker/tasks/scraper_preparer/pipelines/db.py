from scrapy import Spider, Item
from sqlmodel import Session, SQLModel

from cas_worker.db.database import get_session
from cas_worker.db.models.comment import Comment
from cas_worker.db.models.customer import Customer
from cas_worker.db.models.product import Product
from cas_worker.db.models.review import Review
from cas_worker.db.repository import CommentRepository, CustomerRepository, ProductRepository, ReviewRepository
from cas_worker.tasks.scraper_preparer.items import ReviewItem, CommentItem, CustomerItem, ProductItem


class DbPostgresBasePipline(object):
    def __init__(self):
        self.session = None

    def open_spider(self, spider: Spider):
        session: Session = get_session()
        with session.begin() as transaction:
            self.session = session

    def close_spider(self, spider: Spider):
        self.session.close()


class DbPostgresPipeline(DbPostgresBasePipline):
    @staticmethod
    def item_to_model(item: Item, model_obj: SQLModel) -> SQLModel:
        for field in {key for key, value in item.items() if value is not None}:
            model_obj.__setattr__(field, item[field])

    def process_item(self, item: Item, spider: Spider):
        match item:
            case CommentItem():
                item: CommentItem
                comment_repo: CommentRepository = CommentRepository(self.session)
                if comment_repo.get_comment(item['customer_name_id'], item['review_id'], item['reg_datetime']):
                    return item
                comment: Comment = Comment()
                DbPostgresPipeline.item_to_model(item, comment)
                comment_repo.add_comment(comment)
            case CustomerItem():
                item: CustomerItem
                customer_repo: CustomerRepository = CustomerRepository(self.session)
                if customer_repo.get_customer(item['name_id']):
                    return item
                customer: Customer = Customer()
                DbPostgresPipeline.item_to_model(item, customer)
                customer_repo.add_customer(customer)
            case ProductItem():
                item: ProductItem
                product_repo: ProductRepository = ProductRepository(self.session)
                if product_repo.get_product(item['name_id']):
                    return item
                product = Product()
                DbPostgresPipeline.item_to_model(item, product)
                product_repo.add_product(product)
            case ReviewItem():
                item: ReviewItem
                review_repo: ReviewRepository = ReviewRepository(self.session)
                if review_repo.get_review(item['id']):
                    return item
                review: Review = Review()
                DbPostgresPipeline.item_to_model(item, review)
                review_repo.add_review(review)
        return item
