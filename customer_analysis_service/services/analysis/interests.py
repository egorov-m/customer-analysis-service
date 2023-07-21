from sqlalchemy import select
from sqlalchemy.sql.functions import count

from customer_analysis_service.api.v1.schemas.analysis import CustomersForAllCategoriesBaseAnalysis, data_to_schema
from customer_analysis_service.db.models import Review, Comment, Product
from customer_analysis_service.services.analysis.base import BaseService
from customer_analysis_service.services.analysis.enums import ProductCategory


class InterestAnalysisService(BaseService):
    def get_group_customers_interest_for_one_category_by_reviews(self, product_name_id: str,
                                                                 category_number: ProductCategory | int,
                                                                 is_category_above_same_product: bool = False) -> list:
        """
        SELECT ru_category_{number}, href_category_{number}, count(customer_name_id)
        FROM review
        WHERE ru_category_{number} IS NOT NULL AND href_category_{number} IS NOT NULL AND
                    customer_name_id IN (SELECT DISTINCT customer_name_id
                                         FROM review
                                         WHERE evaluated_product_name_id = '{product_name_id}')
        GROUP BY ru_category_{number}, href_category_{number};

        :param product_name_id: analysis product identifier
        :param category_number: category level (from top to bottom): 1, 2, 3, 4
        :param is_category_above_same_product: whether the category above (the digit less (1 to 4)) will be the same as that of the specified product
        :return:
        """
        field_ru = InterestAnalysisService._get_field_category_ru(category_number)
        field_href = InterestAnalysisService._get_field_category_href(category_number)

        with self.session as session:
            subquery = select(Review.customer_name_id).distinct().where(
                Review.evaluated_product_name_id == product_name_id
            )

            where_r = [field_ru.isnot(None),
                       field_href.isnot(None),
                       Review.customer_name_id.in_(subquery)  # we are only looking for reviews for the customers we need
                       ]
            if is_category_above_same_product and 1 < category_number < 5:
                # the level above category must match
                # for example: category 4 - teapots of a particular company, category above 3 - teapots
                above_category = InterestAnalysisService._get_field_category_href(category_number - 1)
                subquery_reviews_on_product = select(above_category).where(Review.evaluated_product_name_id == product_name_id)
                where_r.append(above_category.in_(subquery_reviews_on_product))

            query = (
                select(
                    field_ru,
                    field_href,
                    count(Review.customer_name_id)
                )
                .where(
                    *where_r,
                )
                .group_by(field_ru, field_href)
            )

            return session.exec(query).all()

    def get_group_customers_interest_for_all_categories_by_reviews(self, product_name_id: str) -> list:
        """
        SELECT ru_category_1, href_category_1,
               ru_category_2, href_category_2,
               ru_category_3, href_category_3,
               ru_category_4, href_category_4,
               count(customer_name_id)
        FROM review
        WHERE ru_category_4 IS NOT NULL AND href_category_4 IS NOT NULL AND
        customer_name_id IN (SELECT DISTINCT customer_name_id
                             FROM review
                             WHERE evaluated_product_name_id = '{product_name_id}')
        GROUP BY ru_category_1, href_category_1,
                 ru_category_2, href_category_2,
                 ru_category_3, href_category_3,
                 ru_category_4, href_category_4;

        :param product_name_id: analysis product identifier
        :return:
        """

        field_ru_1 = InterestAnalysisService._get_field_category_ru(1)
        field_href_1 = InterestAnalysisService._get_field_category_href(1)
        field_ru_2 = InterestAnalysisService._get_field_category_ru(2)
        field_href_2 = InterestAnalysisService._get_field_category_href(2)
        field_ru_3 = InterestAnalysisService._get_field_category_ru(3)
        field_href_3 = InterestAnalysisService._get_field_category_href(3)
        field_ru_4 = InterestAnalysisService._get_field_category_ru(4)
        field_href_4 = InterestAnalysisService._get_field_category_href(4)
        p = [field_ru_1, field_href_1,
             field_ru_2, field_href_2,
             field_ru_3, field_href_3,
             field_ru_4, field_href_4, Product.fullname]

        with self.session as session:
            subquery = select(Review.customer_name_id).distinct().where(
                Review.evaluated_product_name_id == product_name_id
            )
            query = (
                select(
                    *p,
                    count(Review.customer_name_id)
                )
                .join(Product, Review.evaluated_product_name_id == Product.name_id)
                .where(
                    # field_ru_3.isnot(None), field_href_3.isnot(None),
                    # field_ru_4.isnot(None), field_href_4.isnot(None),
                    Review.customer_name_id.in_(subquery),
                )
                .group_by(*p)
            )

            result = session.execute(query).all()

            return data_to_schema(result, CustomersForAllCategoriesBaseAnalysis)

    def get_group_customers_interest_for_one_category_by_comments(self, product_name_id: str,
                                                                  category_number: ProductCategory | int,
                                                                  is_category_above_same_product: bool = False) -> list:
        field_ru = InterestAnalysisService._get_field_category_ru(category_number)
        field_href = InterestAnalysisService._get_field_category_href(category_number)
        with self.session as session:
            subquery = select(Comment.customer_name_id).distinct().join(Review, Comment.review_id == Review.id)\
                .where(Review.evaluated_product_name_id == product_name_id)

            where_r = [field_ru.isnot(None),
                       field_href.isnot(None),
                       Comment.customer_name_id.in_(subquery)  # we are only looking for comments for the customers we need
                       ]
            if is_category_above_same_product and 1 < category_number < 5:
                # the level above category must match
                # for example: category 4 - teapots of a particular company, category above 3 - teapots
                above_category = InterestAnalysisService._get_field_category_href(category_number - 1)
                subquery_reviews_on_product = select(above_category).where(
                    Review.evaluated_product_name_id == product_name_id)
                where_r.append(above_category.in_(subquery_reviews_on_product))

            query = (
                select(
                    field_ru,
                    field_href,
                    count(Comment.customer_name_id)
                )
                .join(Review, Comment.review_id == Review.id)
                .where(
                    *where_r
                )
                .group_by(field_ru, field_href)
            )

            return session.execute(query).all()

    def get_group_customers_interest_for_all_categories_by_comments(self, product_name_id: str) -> list:
        field_ru_1 = InterestAnalysisService._get_field_category_ru(1)
        field_href_1 = InterestAnalysisService._get_field_category_href(1)
        field_ru_2 = InterestAnalysisService._get_field_category_ru(2)
        field_href_2 = InterestAnalysisService._get_field_category_href(2)
        field_ru_3 = InterestAnalysisService._get_field_category_ru(3)
        field_href_3 = InterestAnalysisService._get_field_category_href(3)
        field_ru_4 = InterestAnalysisService._get_field_category_ru(4)
        field_href_4 = InterestAnalysisService._get_field_category_href(4)
        p = [field_ru_1, field_href_1,
             field_ru_2, field_href_2,
             field_ru_3, field_href_3,
             field_ru_4, field_href_4, Product.fullname]

        with self.session as session:
            subquery = select(Comment.customer_name_id).distinct().join(Review, Comment.review_id == Review.id)\
                .where(Review.evaluated_product_name_id == product_name_id)

            query = (
                select(
                    *p,
                    count(Comment.customer_name_id)
                )
                .join(Review, Comment.review_id == Review.id)
                .join(Product, Review.evaluated_product_name_id == Product.name_id)
                .where(
                    # field_ru_3.isnot(None), field_href_3.isnot(None),
                    # field_ru_4.isnot(None), field_href_4.isnot(None),
                    Comment.customer_name_id.in_(subquery),
                )
                .group_by(*p)
            )

            result = session.execute(query).all()
            return data_to_schema(result, CustomersForAllCategoriesBaseAnalysis)

    @staticmethod
    def _get_field_category_ru(category_number: ProductCategory | int):
        return getattr(Review, f'ru_category_{category_number}')

    @staticmethod
    def _get_field_category_href(category_number: ProductCategory | int):
        return getattr(Review, f'href_category_{category_number}')
