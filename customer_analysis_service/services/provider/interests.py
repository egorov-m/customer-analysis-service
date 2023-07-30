from sqlalchemy.sql.functions import count
from sqlmodel import Session, select

from customer_analysis_service.api.v1.schemas.analysis import data_to_schema, CustomersForAllCategoriesBaseAnalysis
from customer_analysis_service.db.models import Product, Review, Comment
from customer_analysis_service.services.provider.base import Provider


class InterestsAnalysisProvider(Provider):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_interests_analysis_by_category_of_reviewers(self,
                                                        product_name_id: str
                                                        ) -> list[CustomersForAllCategoriesBaseAnalysis]:
        p = self._get_list_fields_to_group()

        with self.session as session:
            subquery = select(Review.customer_name_id)\
                .distinct()\
                .where(Review.evaluated_product_name_id == product_name_id)

            query = (
                select(*p, count(Review.customer_name_id))
                .join(Product, Review.evaluated_product_name_id == Product.name_id)
                .where(Review.customer_name_id.in_(subquery))
                .group_by(*p)
            )

            result = session.execute(query).all()

            return data_to_schema(result, CustomersForAllCategoriesBaseAnalysis)

    def get_interests_analysis_by_category_of_commentators(self,
                                                           product_name_id: str
                                                           ) -> list[CustomersForAllCategoriesBaseAnalysis]:
        p = self._get_list_fields_to_group()

        with self.session as session:
            subquery = select(Comment.customer_name_id)\
                .distinct()\
                .join(Review, Comment.review_id == Review.id)\
                .where(Review.evaluated_product_name_id == product_name_id)

            query = (
                select(*p, count(Comment.customer_name_id))
                .join(Review, Comment.review_id == Review.id)
                .join(Product, Review.evaluated_product_name_id == Product.name_id)
                .where(Comment.customer_name_id.in_(subquery))
                .group_by(*p)
            )

            result = session.execute(query).all()
            return data_to_schema(result, CustomersForAllCategoriesBaseAnalysis)
