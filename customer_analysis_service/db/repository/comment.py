from datetime import datetime

from sqlmodel import select, Session

from customer_analysis_service.db.models.comment import Comment


class CommentRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def add_comment(self, comment: Comment):
        self.session.add(comment)
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

    def get_all_comments(self) -> list[Comment]:
        return self.session.exec(select(Comment)).all()
