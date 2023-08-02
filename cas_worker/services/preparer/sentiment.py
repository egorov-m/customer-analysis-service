import logging as log
import textwrap

import numpy as np
import torch
from sqlmodel import Session
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from cas_worker.db.models import Review, ReviewSentimentAnalysis, Comment, CommentSentimentAnalysis
from cas_worker.db.repository import ReviewRepository, CommentRepository
from cas_worker.services.preparer.base import Preparer


class SentimentAnalysisPreparer(Preparer):
    logger = log.getLogger('sentiment_analysis_preparer_logger')

    def __init__(self, session: Session):
        super().__init__(session)

        self.tokenizer = AutoTokenizer.from_pretrained("blanchefort/rubert-base-cased-sentiment")
        self.model = AutoModelForSequenceClassification.from_pretrained("blanchefort/rubert-base-cased-sentiment",
                                                                        return_dict=True)
        self.logger.info('SentimentAnalysisPreparer initialized.')

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

        review_repo: ReviewRepository = ReviewRepository(self.session)
        reviews: list[Review] = review_repo.get_all_reviews()
        count: int = 1
        self.logger.info(f'{len(reviews)} reviews found.')

        for review in reviews:
            reviews_sentiment_analysis: list[ReviewSentimentAnalysis] = review_repo.get_reviews_sentiment_analysis_by_review_id(review.id, version_mark)
            sentiment_value: float = self._get_sentiment_analysis_texts(review.text_review)
            if len(reviews_sentiment_analysis) > 0:
                review_sentiment_analysis: ReviewSentimentAnalysis = reviews_sentiment_analysis[0]
                if is_override:

                    review_repo.update_sentiment_value_review_sentiment_analysis(review_sentiment_analysis, sentiment_value)
                    self.logger.info(f'[{count}] Review {review.id} updated: {sentiment_value}')
                else:
                    self.logger.info(f'[{count}] Review {review.id} skipped.')

                count += 1
            else:
                review_sentiment_analysis: ReviewSentimentAnalysis = ReviewSentimentAnalysis()
                review_sentiment_analysis.review_id = review.id
                review_sentiment_analysis.version_mark = version_mark
                review_sentiment_analysis.sentiment_value = sentiment_value
                review_repo.add_review_sentiment_analysis(review_sentiment_analysis)
                self.logger.info(f'[{count}] Sentiment analysis added: {review.id}: {sentiment_value}.')
                count += 1

        self.logger.info('Sentiment analysis of all reviews is complete.')

    def execute_sentiment_analysis_all_comments(self, version_mark: str, is_override: bool = False):
        self.logger.info('Sentiment analysis process launched for all comments.')

        comment_repo: CommentRepository = CommentRepository(self.session)
        comments: list[Comment] = comment_repo.get_all_comments()
        count: int = 1
        self.logger.info(f'{len(comments)} comments found.')

        for comment in comments:
            comments_sentiment_analysis: list[CommentSentimentAnalysis] = comment_repo.get_comments_sentiment_analysis_by_comment_id(comment.id, version_mark)
            if len(comments_sentiment_analysis) > 0:
                comment_sentiment_analysis: CommentSentimentAnalysis = comments_sentiment_analysis[0]
                if is_override:
                    sentiment_value: float = self._get_sentiment_analysis_texts(comment.text_comment)
                    comment_repo.update_sentiment_value_review_sentiment_analysis(comment_sentiment_analysis, sentiment_value)
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
                comment_repo.add_comment_sentiment_analysis(comment_sentiment_analysis)
                self.logger.info(f'[{count}] Sentiment analysis added comment: {comment.id}: {sentiment_value}.')
                count += 1

        self.logger.info('Sentiment analysis of all comments is complete.')
