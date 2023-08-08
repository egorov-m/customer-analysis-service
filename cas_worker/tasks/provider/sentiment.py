from sqlalchemy import func, and_
from sqlmodel import select

from cas_shared.schemas.analysis import GroupRegionallyAllCustomerAnalysis, \
    CustomersForAllCategoriesAnalysis
from cas_shared.schemas.base import data_to_schema_dict
from cas_worker.db.models import RegionalLocation, Customer, ReviewSentimentAnalysis, Review, Comment, \
    CommentSentimentAnalysis, Product
from cas_worker.tasks.provider.base import Provider
from config import WorkerTasks


class SentimentAnalysisCategoryReviewersProvider(Provider):
    def __init__(self):
        super().__init__()
        self.name = self.name = WorkerTasks.analyser_sentiment_category_reviewers

    def run(self, product_name_id: str) -> list[dict]:
        with self.session as session:
            subquery = (
                select(Customer.name_id)
                .join(Review, Customer.name_id == Review.customer_name_id)
                .where(Review.evaluated_product_name_id == product_name_id)
            )

            p = self._get_list_fields_to_group()
            query = (
                select(*p, func.count(Review.id), func.avg(ReviewSentimentAnalysis.sentiment_value))
                .join(Customer, Review.customer_name_id == Customer.name_id)
                .join(Product, Product.name_id == Review.evaluated_product_name_id)
                .join(ReviewSentimentAnalysis, Review.id == ReviewSentimentAnalysis.review_id)
                .where(Customer.name_id.in_(subquery))
                .group_by(*p)
            )

            result = session.execute(query).all()

            return list(data_to_schema_dict(result, CustomersForAllCategoriesAnalysis))


class SentimentAnalysisCategoryCommentatorsProvider(Provider):
    def __init__(self):
        super().__init__()
        self.name = self.name = WorkerTasks.analyser_sentiment_category_commentators

    def run(self, product_name_id: str) -> list[dict]:
        with self.session as session:
            cas_subquery = (
                select(Customer.name_id)
                .join(Comment, Customer.name_id == Comment.customer_name_id)
                .join(Review, Comment.review_id == Review.id)
                .where(Review.evaluated_product_name_id == product_name_id)
                .distinct()
            )

            p = self._get_list_fields_to_group()
            stmt = (
                select(*p, func.count(Customer.name_id), func.avg(CommentSentimentAnalysis.sentiment_value))
                .join(Comment, Customer.name_id == Comment.customer_name_id)
                .join(Review, Comment.review_id == Review.id)
                .join(Product, Review.evaluated_product_name_id == Product.name_id)
                .join(CommentSentimentAnalysis, Comment.id == CommentSentimentAnalysis.comment_id)
                .where(Customer.name_id.in_(cas_subquery))
                .group_by(*p)
            )

            result = session.execute(stmt).all()

            return list(data_to_schema_dict(result, CustomersForAllCategoriesAnalysis))


class SentimentAnalysisRegionallyReviewersProvider(Provider):
    def __init__(self):
        super().__init__()
        self.name = self.name = WorkerTasks.analyser_sentiment_regionally_reviewers

    def run(self, product_name_id: str) -> list[dict]:
        with self.session as session:
            p = self._get_list_region_fields()

            stmt = (
                select(*p, func.count(Customer.name_id), func.avg(ReviewSentimentAnalysis.sentiment_value))
                .join(Customer, and_(Customer.country_ru == RegionalLocation.country_ru,
                                     Customer.city_ru == RegionalLocation.city_ru))
                .join(Review, Review.customer_name_id == Customer.name_id)
                .join(ReviewSentimentAnalysis, ReviewSentimentAnalysis.review_id == Review.id)
                .where(Customer.name_id.in_(
                    select(Customer.name_id).join(Review, Customer.name_id == Review.customer_name_id).where(
                        Review.evaluated_product_name_id == product_name_id)))
                .group_by(*p)
            )

            result = session.execute(stmt).all()

            return list(data_to_schema_dict(result, GroupRegionallyAllCustomerAnalysis))


class SentimentAnalysisRegionallyCommentatorsProvider(Provider):
    def __init__(self):
        super().__init__()
        self.name = self.name = WorkerTasks.analyser_sentiment_regionally_commentators

    def run(self, product_name_id: str) -> list[dict]:
        with self.session as session:
            subquery = (
                select(Comment.customer_name_id).distinct()
                .join(Customer, Customer.name_id == Comment.customer_name_id)
                .join(Review, Comment.review_id == Review.id)
                .where(Review.evaluated_product_name_id == product_name_id)
            )

            p = self._get_list_region_fields()
            stmt = (
                select(*p, func.count(Customer.name_id), func.avg(CommentSentimentAnalysis.sentiment_value))
                .join(Customer, and_(Customer.country_ru == RegionalLocation.country_ru,
                                     Customer.city_ru == RegionalLocation.city_ru))
                .join(Comment, Customer.name_id == Comment.customer_name_id)
                .join(CommentSentimentAnalysis, Comment.id == CommentSentimentAnalysis.comment_id)
                .where(Customer.name_id.in_(subquery))
                .group_by(*p)
            )

            result = session.execute(stmt).all()

            return list(data_to_schema_dict(result, GroupRegionallyAllCustomerAnalysis))
