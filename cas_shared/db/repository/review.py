from sqlmodel import select, Session

from cas_shared.db.models.review import Review, ReviewSentimentAnalysis
from cas_shared.db.utils import menage_db_method, CommitMode


class ReviewRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    @menage_db_method(CommitMode.FLUSH)
    def add_review(self, review: Review):
        self.session.add(review)

    @menage_db_method(CommitMode.FLUSH)
    def add_review_sentiment_analysis(self, review_sentiment_analysis: ReviewSentimentAnalysis):
        self.session.add(review_sentiment_analysis)

    def get_review(self, review_id: int) -> Review:
        return self.session.get(Review, review_id)

    def get_reviews_sentiment_analysis_by_review_id(self, review_id: int, version_mark: str = None) -> list[ReviewSentimentAnalysis]:
        st = select(ReviewSentimentAnalysis).where(ReviewSentimentAnalysis.review_id == review_id)
        if version_mark is not None:
            st.where(ReviewSentimentAnalysis.version_mark == version_mark)

        res = self.session.execute(st).scalars()
        return res.all()

    def get_reviews_sentiment_analysis_by_version_mark(self, version_mark: str) -> list[ReviewSentimentAnalysis]:
        st = select(ReviewSentimentAnalysis).where(ReviewSentimentAnalysis.version_mark == version_mark)
        res = self.session.execute(st).scalars()
        return res.all()

    @menage_db_method(CommitMode.FLUSH)
    def update_sentiment_value_review_sentiment_analysis(self,
                                                         review_sentiment_analysis: ReviewSentimentAnalysis,
                                                         sentiment_value: float):
        review_sentiment_analysis.sentiment_value = sentiment_value
        self.session.add(review_sentiment_analysis)

    def get_all_reviews(self) -> list[Review]:
        res = self.session.execute(select(Review)).scalars()
        return res.all()

    def get_all_reviews_for_product(self, product_name_id: str) -> list[Review]:
        st = select(Review).where(Review.evaluated_product_name_id == product_name_id)
        res = self.session.execute(st).scalars()
        return res.all()

    def get_all_reviews_for_customer(self, customer_name_id: str) -> list[Review]:
        st = select(Review).where(Review.customer_name_id == customer_name_id)
        res = self.session.execute(st).scalars()
        return res.all()

    @menage_db_method(CommitMode.FLUSH)
    def update_state_all_commenting_customers_available(self, review: Review, new_state: bool):
        review.is_all_commenting_customers_available = new_state
        self.session.add(review)
