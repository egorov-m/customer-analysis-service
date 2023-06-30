from sqlalchemy.future.engine import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from sqlmodel.engine.create import create_engine as _create_engine
from sqlmodel import Session


from .repository import (
    CommentRepository,
    CustomerRepository,
    ProductRepository,
    ReviewRepository
)


def create_engine(url: URL | str, echo: bool = False) -> Engine:
    """
    Creating database engine
    :param url Address for connection in the database
    :param echo Output SQL queries to the standard output stream
    :return:
    """
    return _create_engine(url=url, echo=echo, encoding='utf-8')


def get_session_maker(engine: Engine | None = None) -> sessionmaker:
    return sessionmaker(engine, class_=Session)


class Database:

    session: Session

    def __init__(self,
                 session: Session,
                 comment: CommentRepository = None,
                 customer: CustomerRepository = None,
                 product: ProductRepository = None,
                 review: ReviewRepository = None):

        self.session = session
        self.comment = comment or CommentRepository(session=session)
        self.customer = customer or CustomerRepository(session=session)
        self.product = product or ProductRepository(session=session)
        self.review = review or ReviewRepository(session=session)
