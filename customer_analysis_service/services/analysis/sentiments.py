import logging as log
import textwrap

import torch
import numpy as np
from sqlalchemy import and_, join, func
from sqlmodel import select
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from customer_analysis_service.db import Database
from customer_analysis_service.db.models import Review, Comment, ReviewSentimentAnalysis, CommentSentimentAnalysis, \
    RegionalLocation, Customer, Product
from customer_analysis_service.services.analysis.base import BaseService


class SentimentAnalysisService(BaseService):
    logger = log.getLogger('sentiment_analysis_service_logger')

    def __init__(self, database: Database):
        super().__init__(database)
        self.tokenizer = AutoTokenizer.from_pretrained("blanchefort/rubert-base-cased-sentiment")
        self.model = AutoModelForSequenceClassification.from_pretrained("blanchefort/rubert-base-cased-sentiment", return_dict=True)
        self.logger.info('SentimentAnalysisService initialized.')

    @torch.no_grad()
    def _get_sentiment_analysis_texts(self, text: str) -> float:
        """
        Default labels: 0: NEUTRAL 1: POSITIVE 2: NEGATIVE
        Replacing for NEGATIVE
        Used labels: 0: NEUTRAL 1: POSITIVE -1: NEGATIVE
        :param text:
        :return:
        """
        max_length = 512
        chunks = textwrap.wrap(text, max_length)
        res: float = 0
        for c in chunks:
            inputs = self.tokenizer(c, max_length=max_length, padding=True, truncation=True, return_tensors='pt')
            outputs = self.model(**inputs)
            # applies the softmax function to the model output to obtain class probabilities
            predicted = torch.nn.functional.softmax(outputs.logits, dim=1)
            # argmax to get the index of the class with the highest probability
            predicted: np.ndarray = torch.argmax(predicted, dim=1).numpy()
            predicted = [-1 if x == 2 else x for x in predicted]
            res += float(predicted[0])

        return res / len(chunks)

    def execute_sentiment_analysis_all_reviews(self, version_mark: str, is_override: bool = False):
        self.logger.info('Sentiment analysis process launched for all reviews.')

        reviews: list[Review] = self.database.review.get_all_reviews()
        count: int = 1
        self.logger.info(f'{len(reviews)} reviews found.')

        for review in reviews:
            reviews_sentiment_analysis: list[ReviewSentimentAnalysis] = self.database.review.get_reviews_sentiment_analysis_by_review_id(review.id, version_mark)
            sentiment_value: float = self._get_sentiment_analysis_texts(review.text_review)
            if len(reviews_sentiment_analysis) > 0:
                review_sentiment_analysis: ReviewSentimentAnalysis = reviews_sentiment_analysis[0]
                if is_override:

                    self.database.review.update_sentiment_value_review_sentiment_analysis(review_sentiment_analysis, sentiment_value)
                    self.logger.info(f'[{count}] Review {review.id} updated: {sentiment_value}')
                else:
                    self.logger.info(f'[{count}] Review {review.id} skipped.')

                count += 1
            else:
                review_sentiment_analysis: ReviewSentimentAnalysis = ReviewSentimentAnalysis()
                review_sentiment_analysis.review_id = review.id
                review_sentiment_analysis.version_mark = version_mark
                review_sentiment_analysis.sentiment_value = sentiment_value
                self.database.review.add_review_sentiment_analysis(review_sentiment_analysis)
                self.logger.info(f'[{count}] Sentiment analysis added: {review.id}: {sentiment_value}.')
                count += 1

        self.logger.info('Sentiment analysis of all reviews is complete.')

    def execute_sentiment_analysis_all_comments(self, version_mark: str, is_override: bool = False):
        self.logger.info('Sentiment analysis process launched for all comments.')

        comments: list[Comment] = self.database.comment.get_all_comments()
        count: int = 1
        self.logger.info(f'{len(comments)} comments found.')

        for comment in comments:
            comments_sentiment_analysis: list[CommentSentimentAnalysis] = self.database.comment.get_comments_sentiment_analysis_by_comment_id(comment.id, version_mark)
            if len(comments_sentiment_analysis) > 0:
                comment_sentiment_analysis: CommentSentimentAnalysis = comments_sentiment_analysis[0]
                if is_override:
                    sentiment_value: float = self._get_sentiment_analysis_texts(comment.text_comment)
                    self.database.comment.update_sentiment_value_review_sentiment_analysis(comment_sentiment_analysis, sentiment_value)
                    self.logger.info(f'[{count}] Comment {comment.id} updated: {sentiment_value}')
                else:
                    self.logger.info(f'[{count}] Comment {comment.id} skipped.')

                count += 1
            else:
                sentiment_value: float = self._get_sentiment_analysis_texts(comment.text_comment)
                comment_sentiment_analysis: CommentSentimentAnalysis = CommentSentimentAnalysis()
                comment_sentiment_analysis.comment_id = comment.id
                comment_sentiment_analysis.version_mark = version_mark
                comment_sentiment_analysis.sentiment_value = sentiment_value
                self.database.comment.add_comment_sentiment_analysis(comment_sentiment_analysis)
                self.logger.info(f'[{count}] Sentiment analysis added comment: {comment.id}: {sentiment_value}.')
                count += 1

        self.logger.info('Sentiment analysis of all comments is complete.')

    def get_sentiment_analysis_regionally_all_products_reviews(self, product_name_id: str):
        """
        Получить сентимент анализ для регионов по всем отывам по указанному продукту

        SELECT rl.country_ru, rl.country_en, rl.city_ru, rl.city_en, rl.latitude, rl.longitude, rsa.sentiment_value FROM review rv
        JOIN customer c on c.name_id = rv.customer_name_id
        JOIN regional_location rl on c.country_ru = rl.country_ru AND c.city_ru = rl.city_ru
        JOIN review_sentiment_analysis rsa on rv.id = rsa.review_id
        WHERE rv.evaluated_product_name_id = 'product_name_id';

        :param product_name_id:
        :return:
        """
        with self.database.session as session:
            join_condition = join(Review, Customer, Customer.name_id == Review.customer_name_id)\
                .join(RegionalLocation, and_(Customer.country_ru == RegionalLocation.country_ru,
                                             Customer.city_ru == RegionalLocation.city_ru))\
                .join(ReviewSentimentAnalysis, Review.id == ReviewSentimentAnalysis.review_id)

            stmt = select(
                RegionalLocation.country_ru,
                RegionalLocation.country_en,
                RegionalLocation.city_ru,
                RegionalLocation.city_en,
                RegionalLocation.latitude,
                RegionalLocation.longitude,
                ReviewSentimentAnalysis.sentiment_value
            ).select_from(join_condition).where(
                Review.evaluated_product_name_id == product_name_id
            )

            return session.exec(stmt).all()

    def get_sentiment_analysis_regionally_all_products_comments(self, product_name_id: str):
        """
        Получить сентимент анализ для регионам по всем отзывам по указанному продукту

        SELECT rl.country_ru, rl.country_en, rl.city_ru, rl.city_en, rl.latitude, rl.longitude, rsa.sentiment_value
        FROM comment JOIN review r on comment.review_id = r.id
                     JOIN customer cus ON comment.customer_name_id = cus.name_id
                     JOIN review_sentiment_analysis rsa on r.id = rsa.review_id
                     JOIN regional_location rl on cus.country_ru = rl.country_ru AND cus.city_ru = rl.city_ru
        WHERE r.evaluated_product_name_id = 'product_name_id';

        :param product_name_id:
        :return:
        """
        with self.database.session as session:
            stmt = (
                select(
                    RegionalLocation.country_ru,
                    RegionalLocation.country_en,
                    RegionalLocation.city_ru,
                    RegionalLocation.city_en,
                    RegionalLocation.latitude,
                    RegionalLocation.longitude,
                    ReviewSentimentAnalysis.sentiment_value,
                )
                .join(Customer, and_(Customer.country_ru == RegionalLocation.country_ru,
                                     Customer.city_ru == RegionalLocation.city_ru))
                .join(Comment, Comment.customer_name_id == Customer.name_id)
                .join(Review, Comment.review_id == Review.id)
                .join(ReviewSentimentAnalysis, Review.id == ReviewSentimentAnalysis.review_id)
                .where(Review.evaluated_product_name_id == product_name_id)
            )

            return session.exec(stmt).all()

    def get_sentiment_analysis_group_regionally_all_customer_reviews_product(self, product_name_id: str):
        """
        Получить сентимент анализ сгруппированный по ругионам для всех отзывов клиентов нашего продукта

        SELECT rl.country_ru, rl.country_en, rl.city_ru, rl.city_en, rl.latitude, rl.longitude, count(c.name_id), avg(rsa.sentiment_value) FROM customer c
                   JOIN regional_location rl on c.country_ru = rl.country_ru AND c.city_ru = rl.city_ru
                   JOIN review r on r.customer_name_id = c.name_id
                   JOIN review_sentiment_analysis rsa on r.id = rsa.review_id
        WHERE c.name_id in (SELECT ca.name_id FROM customer ca JOIN review rv ON ca.name_id = rv.customer_name_id
                    WHERE rv.evaluated_product_name_id = 'product_name_id')
        GROUP BY rl.country_ru, rl.country_en, rl.city_ru, rl.city_en, rl.latitude, rl.longitude;

        :param product_name_id:
        :return:
        """
        with self.database.session as session:
            stmt = (
                select(
                    RegionalLocation.country_ru,
                    RegionalLocation.country_en,
                    RegionalLocation.city_ru,
                    RegionalLocation.city_en,
                    RegionalLocation.latitude,
                    RegionalLocation.longitude,
                    func.count(Customer.name_id),  # количество отзывов в регионе
                    func.avg(ReviewSentimentAnalysis.sentiment_value),  # среднее значение сентимент анализа для региона по отзывам
                )
                .join(Customer, and_(Customer.country_ru == RegionalLocation.country_ru,
                                     Customer.city_ru == RegionalLocation.city_ru))
                .join(Review, Review.customer_name_id == Customer.name_id)
                .join(ReviewSentimentAnalysis, ReviewSentimentAnalysis.review_id == Review.id)
                .where(Customer.name_id.in_(
                    select(Customer.name_id).join(Review, Customer.name_id == Review.customer_name_id).where(
                        Review.evaluated_product_name_id == product_name_id)))
                .group_by(
                    RegionalLocation.country_ru,
                    RegionalLocation.country_en,
                    RegionalLocation.city_ru,
                    RegionalLocation.city_en,
                    RegionalLocation.latitude,
                    RegionalLocation.longitude,
                )
            )

            return session.exec(stmt).all()

    def get_sentiment_analysis_group_regionally_all_customer_comments_product(self, product_name_id: str):
        """
        Получить сентимент анализ сгруппированный по ругионам для всех омментариев клиентов нашего продукта

        SELECT rl.country_ru, rl.country_en, rl.city_ru, rl.city_en, rl.latitude, rl.longitude, count(c.name_id), avg(csa.sentiment_value) FROM customer c
                   JOIN regional_location rl on c.country_ru = rl.country_ru AND c.city_ru = rl.city_ru
                   JOIN comment com on c.name_id = com.customer_name_id
                   JOIN comment_sentiment_analysis csa on com.id = csa.comment_id
        WHERE c.name_id in (SELECT DISTINCT cas.name_id FROM customer cas JOIN comment co ON cas.name_id = co.customer_name_id
                                                                   JOIN review rv ON co.review_id = rv.id
                            WHERE rv.evaluated_product_name_id = 'product_name_id')
        GROUP BY rl.country_ru, rl.country_en, rl.city_ru, rl.city_en, rl.latitude, rl.longitude;

        :param product_name_id:
        :return:
        """
        with self.database.session as session:
            subquery = (
                select(Comment.customer_name_id).distinct()
                .join(Customer, Customer.name_id == Comment.customer_name_id)
                .join(Review, Comment.review_id == Review.id)
                .where(Review.evaluated_product_name_id == product_name_id)
            )

            stmt = (
                select(
                    RegionalLocation.country_ru,
                    RegionalLocation.country_en,
                    RegionalLocation.city_ru,
                    RegionalLocation.city_en,
                    RegionalLocation.latitude,
                    RegionalLocation.longitude,
                    func.count(Customer.name_id),  # количество комментариев в регионе
                    func.avg(CommentSentimentAnalysis.sentiment_value),  # среднее значение сентимент анализа для региона по комментарием
                )
                .join(Customer, and_(Customer.country_ru == RegionalLocation.country_ru,
                                     Customer.city_ru == RegionalLocation.city_ru))
                .join(Comment, Customer.name_id == Comment.customer_name_id)
                .join(CommentSentimentAnalysis, Comment.id == CommentSentimentAnalysis.comment_id)
                .where(Customer.name_id.in_(subquery))
                .group_by(
                    RegionalLocation.country_ru,
                    RegionalLocation.country_en,
                    RegionalLocation.city_ru,
                    RegionalLocation.city_en,
                    RegionalLocation.latitude,
                    RegionalLocation.longitude,
                )
            )

            return session.exec(stmt).all()

    def get_sentiment_analysis_customer_reviews_product_grouped_by_category(self, product_name_id: str):
        """
        Получить сенитмент анализ отзывов клиентов указанного продукта сгруппированный по категориям

        SELECT r.ru_category_1, r.href_category_1, r.ru_category_2, r.href_category_2,
         r.ru_category_3, r.href_category_3, r.ru_category_4, r.href_category_4, p.fullname, count(r.id), avg(rsa.sentiment_value)
        FROM customer c JOIN review r on r.customer_name_id = c.name_id
                        JOIN product p on p.name_id = r.evaluated_product_name_id
                        JOIN review_sentiment_analysis rsa on r.id = rsa.review_id
        WHERE c.name_id in (SELECT ca.name_id FROM customer ca JOIN review rv ON ca.name_id = rv.customer_name_id
                            WHERE rv.evaluated_product_name_id = 'product_name_id')
        GROUP BY r.ru_category_1, r.href_category_1,
                 r.ru_category_2, r.href_category_2,
                 r.ru_category_3, r.href_category_3,
                 r.ru_category_4, r.href_category_4, p.fullname;

        :param product_name_id:
        :return:
        """
        with self.database.session as session:
            subquery = (
                select(Customer.name_id)
                .join(Review, Customer.name_id == Review.customer_name_id)
                .where(Review.evaluated_product_name_id == product_name_id)
            )

            query = (
                select(
                    Review.ru_category_1,
                    Review.href_category_1,
                    Review.ru_category_2,
                    Review.href_category_2,
                    Review.ru_category_3,
                    Review.href_category_3,
                    Review.ru_category_4,
                    Review.href_category_4,
                    Product.fullname,
                    func.count(Review.id),
                    func.avg(ReviewSentimentAnalysis.sentiment_value)
                )
                .join(Customer, Review.customer_name_id == Customer.name_id)
                .join(Product, Product.name_id == Review.evaluated_product_name_id)
                .join(ReviewSentimentAnalysis, Review.id == ReviewSentimentAnalysis.review_id)
                .where(Customer.name_id.in_(subquery))
                .group_by(
                    Review.ru_category_1,
                    Review.href_category_1,
                    Review.ru_category_2,
                    Review.href_category_2,
                    Review.ru_category_3,
                    Review.href_category_3,
                    Review.ru_category_4,
                    Review.href_category_4,
                    Product.fullname
                )
            )

            return session.exec(query).all()

    def get_sentiment_analysis_customer_comments_product_grouped_by_category(self, product_name_id: str):
        """
        Получить сенитмент анализ комментариев клиентов указанного продукта сгруппированный по категориям

        SELECT rev.ru_category_1, rev.href_category_1,
               rev.ru_category_2, rev.href_category_2,
               rev.ru_category_3, rev.href_category_3,
               rev.ru_category_4, rev.href_category_4, count(c.name_id), avg(csa.sentiment_value)
        FROM customer c JOIN comment com on c.name_id = com.customer_name_id
                        JOIN review rev on com.review_id = rev.id
                        JOIN comment_sentiment_analysis csa on com.id = csa.comment_id
        WHERE c.name_id in (SELECT DISTINCT cas.name_id
                            FROM customer cas JOIN comment co ON cas.name_id = co.customer_name_id
                                              JOIN review rv ON co.review_id = rv.id
                            WHERE rv.evaluated_product_name_id = 'product_name_id')
        GROUP BY rev.ru_category_1, rev.href_category_1,
                 rev.ru_category_2, rev.href_category_2,
                 rev.ru_category_3, rev.href_category_3,
                 rev.ru_category_4, rev.href_category_4;

        :param product_name_id:
        :return:
        """
        with self.database.session as session:
            cas_subquery = (
                select(Customer.name_id)
                .join(Comment, Customer.name_id == Comment.customer_name_id)
                .join(Review, Comment.review_id == Review.id)
                .where(Review.evaluated_product_name_id == product_name_id)
                .distinct()
            )

            stmt = (
                select(
                    Review.ru_category_1,
                    Review.href_category_1,
                    Review.ru_category_2,
                    Review.href_category_2,
                    Review.ru_category_3,
                    Review.href_category_3,
                    Review.ru_category_4,
                    Review.href_category_4,
                    func.count(Customer.name_id),
                    func.avg(CommentSentimentAnalysis.sentiment_value),
                )
                .join(Comment, Customer.name_id == Comment.customer_name_id)
                .join(Review, Comment.review_id == Review.id)
                .join(CommentSentimentAnalysis, Comment.id == CommentSentimentAnalysis.comment_id)
                .where(Customer.name_id.in_(cas_subquery))
                .group_by(
                    Review.ru_category_1,
                    Review.href_category_1,
                    Review.ru_category_2,
                    Review.href_category_2,
                    Review.ru_category_3,
                    Review.href_category_3,
                    Review.ru_category_4,
                    Review.href_category_4,
                )
            )

            return session.exec(stmt).all()
