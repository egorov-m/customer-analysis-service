from sqlalchemy import func
from sqlmodel import select

from cas_shared.schemas.analysis import CustomerReputationAnalysisValue, CustomersForAllCategoriesAnalysis
from cas_shared.schemas.base import data_to_schema_dict
from cas_worker.db.models import Comment, Review, Customer, CustomerSimilarityAnalysis, Product
from cas_worker.tasks.analysis_provider.base import Provider
from cas_worker.tasks.analysis_provider.utils import manage_result_size
from config import WorkerTasks


class SimilarityAnalysisReputationReviewersProvider(Provider):
    def __init__(self):
        super().__init__()
        self.name = WorkerTasks.analyser_similarity_reputation_reviewers

    @manage_result_size()
    def run(self, product_name_id: str) -> list[dict]:
        with self.session as session:
            subquery = select(Review.customer_name_id).distinct()\
                .where(Review.evaluated_product_name_id == product_name_id)

            query = select(Customer.reputation, CustomerSimilarityAnalysis.similarity_reviews_value)\
                .join(Customer, CustomerSimilarityAnalysis.customer_name_id == Customer.name_id)\
                .where(Customer.name_id.in_(subquery))

            result = session.execute(query).all()

            return list(data_to_schema_dict(result, CustomerReputationAnalysisValue))


class SimilarityAnalysisReputationCommentatorsProvider(Provider):
    def __init__(self):
        super().__init__()
        self.name = WorkerTasks.analyser_similarity_reputation_commentators

    @manage_result_size()
    def run(self, product_name_id: str) -> list[dict]:
        with self.session as session:
            subquery = select(Comment.customer_name_id).distinct()\
                .join(Review, Comment.review_id == Review.id)\
                .where(Review.evaluated_product_name_id == product_name_id)

            query = select(Customer.reputation, CustomerSimilarityAnalysis.similarity_comments_value).\
                join(Customer, CustomerSimilarityAnalysis.customer_name_id == Customer.name_id)\
                .where(Customer.name_id.in_(subquery))

            result = session.execute(query).all()

            return list(data_to_schema_dict(result, CustomerReputationAnalysisValue))


class SimilarityAnalysisCategoryReviewersProvider(Provider):
    def __init__(self):
        super().__init__()
        self.name = WorkerTasks.analyser_similarity_category_reviewers

    @manage_result_size()
    def run(self, product_name_id: str) -> list[dict]:
        with self.session as session:
            subquery = (
                select(Customer.name_id)
                .join(Review, Customer.name_id == Review.customer_name_id)
                .where(Review.evaluated_product_name_id == product_name_id)
            )

            p = self._get_list_fields_to_group()
            query = (
                select(*p, func.count(Review.id), func.avg(CustomerSimilarityAnalysis.similarity_reviews_value))
                .join(Customer, Review.customer_name_id == Customer.name_id)
                .join(Product, Product.name_id == Review.evaluated_product_name_id)
                .join(CustomerSimilarityAnalysis, Customer.name_id == CustomerSimilarityAnalysis.customer_name_id)
                .where(Customer.name_id.in_(subquery))
                .group_by(*p)
            )

            result = session.execute(query).all()

            return list(data_to_schema_dict(result, CustomersForAllCategoriesAnalysis))


class SimilarityAnalysisCategoryCommentatorsProvider(Provider):
    def __init__(self):
        super().__init__()
        self.name = WorkerTasks.analyser_similarity_category_commentators

    @manage_result_size()
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
                select(*p, func.count(Customer.name_id), func.avg(CustomerSimilarityAnalysis.similarity_comments_value))
                .join(Comment, Customer.name_id == Comment.customer_name_id)
                .join(Review, Comment.review_id == Review.id)
                .join(Product, Review.evaluated_product_name_id == Product.name_id)
                .join(CustomerSimilarityAnalysis, Customer.name_id == CustomerSimilarityAnalysis.customer_name_id)
                .where(Customer.name_id.in_(cas_subquery))
                .group_by(*p)
            )

            result = session.execute(stmt).all()

            return list(data_to_schema_dict(result, CustomersForAllCategoriesAnalysis))
