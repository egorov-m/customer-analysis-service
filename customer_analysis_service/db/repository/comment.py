from datetime import datetime

from sqlmodel import select, Session

from customer_analysis_service.db.models.comment import Comment, CommentSentimentAnalysis


class CommentRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def add_comment(self, comment: Comment):
        self.session.add(comment)
        self.session.commit()

    def add_comment_sentiment_analysis(self, comment_sentiment_analysis: CommentSentimentAnalysis):
        self.session.add(comment_sentiment_analysis)
        self.session.commit()

    def get_comment_by_id(self, comment_id: str) -> Comment:
        return self.session.exec(select(Comment).where(Comment.id == comment_id)).first()

    def get_comment(self, customer_name_id: str, review_id: int, reg_datetime: datetime) -> Comment:
        """
        Comments on an external resource do not have any identifiers.
        The PK Id is only in the database.
        We use the other fields as a composite key.
        :param customer_name_id:
        :param review_id:
        :param reg_datetime:
        :return:
        """
        return self.session.exec(select(Comment).where(Comment.customer_name_id == customer_name_id)
                                 .where(Comment.review_id == review_id)
                                 .where(Comment.reg_datetime == reg_datetime)).first()

    def get_comments_sentiment_analysis_by_comment_id(self, comment_id: int, version_mark: str = None) -> list[CommentSentimentAnalysis]:
        query = select(CommentSentimentAnalysis).where(CommentSentimentAnalysis.comment_id == comment_id)
        if version_mark is not None:
            query.where(CommentSentimentAnalysis.version_mark == version_mark)

        return self.session.exec(query).all()

    def get_comments_sentiment_analysis_by_version_mark(self, version_mark: str) -> list[CommentSentimentAnalysis]:
        return self.session.exec(select(CommentSentimentAnalysis)
                                 .where(CommentSentimentAnalysis.version_mark == version_mark)).all()

    def update_sentiment_value_review_sentiment_analysis(self,
                                                         review_sentiment_analysis: CommentSentimentAnalysis,
                                                         sentiment_value: float):
        review_sentiment_analysis.sentiment_value = sentiment_value
        self.session.add(review_sentiment_analysis)
        self.session.commit()

    def get_all_comments(self) -> list[Comment]:
        return self.session.exec(select(Comment)).all()
