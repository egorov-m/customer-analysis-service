from sqlalchemy.sql.functions import count
from sqlmodel import select

from cas_shared.schemas.analysis import CustomersForAllCategoriesBaseAnalysis
from cas_shared.schemas.base import data_to_schema_dict
from cas_shared.db.models import Product, Review, Comment
from cas_worker.tasks.analysis_provider.base import Provider
from cas_worker.tasks.analysis_provider.utils import manage_result_size
from config import WorkerTasks


class InterestsAnalysisReviewersProvider(Provider):
    def __init__(self):
        super().__init__()
        self.name = WorkerTasks.analyser_interests_reviewers

    @manage_result_size()
    def run(self, product_name_id: str) -> list[dict]:
        p = self._get_list_fields_to_group()

        with self.session as session:
            subquery = select(Review.customer_name_id) \
                .distinct() \
                .where(Review.evaluated_product_name_id == product_name_id)

            query = (
                select(*p, count(Review.customer_name_id))
                .join(Product, Review.evaluated_product_name_id == Product.name_id)
                .where(Review.customer_name_id.in_(subquery))
                .group_by(*p)
            )

            result = session.execute(query).all()

            return list(data_to_schema_dict(result, CustomersForAllCategoriesBaseAnalysis))


class InterestsAnalysisCommentatorsProvider(Provider):
    def __init__(self):
        super().__init__()
        self.name = WorkerTasks.analyser_interests_commentators

    @manage_result_size()
    def run(self, product_name_id: str) -> list[dict]:
        p = self._get_list_fields_to_group()

        with self.session as session:
            subquery = select(Comment.customer_name_id) \
                .distinct() \
                .join(Review, Comment.review_id == Review.id) \
                .where(Review.evaluated_product_name_id == product_name_id)

            query = (
                select(*p, count(Comment.customer_name_id))
                .join(Review, Comment.review_id == Review.id)
                .join(Product, Review.evaluated_product_name_id == Product.name_id)
                .where(Comment.customer_name_id.in_(subquery))
                .group_by(*p)
            )

            result = session.execute(query).all()

            return list(data_to_schema_dict(result, CustomersForAllCategoriesBaseAnalysis))
