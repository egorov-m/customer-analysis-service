from sqlmodel import Session, select

from cas_shared.schemas.analysis import data_to_schema, CustomerReputationAnalysisValue
from cas_worker.db.models import Comment, Review, Customer, CustomerSimilarityAnalysis
from cas_worker.tests.provider.base import Provider


class SimilarityAnalysisProvider(Provider):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_similarity_analysis_by_reputation_of_commentators(self,
                                                              product_name_id: str) -> list[CustomerReputationAnalysisValue]:
        with self.session as session:
            subquery = select(Comment.customer_name_id).distinct()\
                .join(Review, Comment.review_id == Review.id)\
                .where(Review.evaluated_product_name_id == product_name_id)

            query = select(Customer.reputation, CustomerSimilarityAnalysis.similarity_comments_value).\
                join(Customer, CustomerSimilarityAnalysis.customer_name_id == Customer.name_id)\
                .where(Customer.name_id.in_(subquery))

            result = session.execute(query).all()

            return data_to_schema(result, CustomerReputationAnalysisValue)

    def get_similarity_analysis_by_reputation_of_reviewers(self,
                                                           product_name_id: str) -> list[CustomerReputationAnalysisValue]:
        with self.session as session:
            subquery = select(Review.customer_name_id).distinct()\
                .where(Review.evaluated_product_name_id == product_name_id)

            query = select(Customer.reputation, CustomerSimilarityAnalysis.similarity_reviews_value)\
                .join(Customer, CustomerSimilarityAnalysis.customer_name_id == Customer.name_id)\
                .where(Customer.name_id.in_(subquery))

            result = session.execute(query).all()

            return data_to_schema(result, CustomerReputationAnalysisValue)
