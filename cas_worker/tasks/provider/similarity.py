from sqlmodel import select

from cas_shared.schemas.analysis import CustomerReputationAnalysisValue, data_to_schema_dict
from cas_worker.db.models import Comment, Review, Customer, CustomerSimilarityAnalysis
from cas_worker.tasks.provider.base import Provider
from config import WorkerTasks


class SimilarityAnalysisReputationReviewersProvider(Provider):
    def __init__(self):
        super().__init__()
        self.name = self.name = WorkerTasks.analyser_similarity_reputation_reviewers

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
        self.name = self.name = WorkerTasks.analyser_similarity_reputation_commentators

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
