from sqlmodel import select, Session

from customer_analysis_service.db.models.review import Review


class ReviewRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def add_review(self, review: Review):
        self.session.add(review)
        self.session.commit()

    def get_review(self, review_id: int) -> Review:
        return self.session.execute(select(Review).where(Review.id == review_id))

    def get_all_reviews(self) -> list[Review]:
        return self.session.execute(select(Review))
