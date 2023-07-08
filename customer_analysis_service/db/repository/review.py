from sqlmodel import select, Session

from customer_analysis_service.db.models.review import Review, ReviewSentimentAnalysis


class ReviewRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def add_review(self, review: Review):
        self.session.add(review)
        self.session.commit()

    def add_review_sentiment_analysis(self, review_sentiment_analysis: ReviewSentimentAnalysis):
        self.session.add(review_sentiment_analysis)
        self.session.commit()

    def get_review(self, review_id: int) -> Review:
        return self.session.exec(select(Review).where(Review.id == review_id)).first()

    def get_reviews_sentiment_analysis_by_review_id(self, review_id: int, version_mark: str = None) -> list[ReviewSentimentAnalysis]:
        query = select(ReviewSentimentAnalysis).where(ReviewSentimentAnalysis.review_id == review_id)
        if version_mark is not None:
            query.where(ReviewSentimentAnalysis.version_mark == version_mark)

        return self.session.exec(query).all()

    def get_reviews_sentiment_analysis_by_version_mark(self, version_mark: str) -> list[ReviewSentimentAnalysis]:
        return self.session.exec(select(ReviewSentimentAnalysis)
                                 .where(ReviewSentimentAnalysis.version_mark == version_mark)).all()

    def update_sentiment_value_review_sentiment_analysis(self,
                                                         review_sentiment_analysis: ReviewSentimentAnalysis,
                                                         sentiment_value: float):
        review_sentiment_analysis.sentiment_value = sentiment_value
        self.session.add(review_sentiment_analysis)
        self.session.commit()

    def get_all_reviews(self) -> list[Review]:
        return self.session.exec(select(Review)).all()

    def update_state_all_commenting_customers_available(self, review: Review, new_state: bool):
        review.is_all_commenting_customers_available = new_state
        self.session.add(review)
        self.session.commit()
