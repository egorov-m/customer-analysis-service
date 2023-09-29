from typing import Optional

from sqlmodel import select, Session

from cas_shared.db.models.customer import Customer, CustomerSimilarityAnalysis
from cas_shared.db.utils import menage_db_method, CommitMode


class CustomerRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    @menage_db_method(CommitMode.FLUSH)
    def add_customer(self, customer: Customer):
        self.session.add(customer)

    @menage_db_method(CommitMode.FLUSH)
    def add_product_sentiment_analysis(self, customer_sentiment_analysis: CustomerSimilarityAnalysis):
        self.session.add(customer_sentiment_analysis)

    def get_customer(self, name_id: str) -> Customer:
        return self.session.get(Customer, name_id)

    def get_all_customers(self) -> list[Customer]:
        res = self.session.execute(select(Customer)).scalars()
        return res.all()

    def get_customers_similarity_analysis(self, customer_name_id: str, version_mark: str = None):
        st = select(CustomerSimilarityAnalysis).where(CustomerSimilarityAnalysis.customer_name_id == customer_name_id)
        if version_mark is not None:
            st.where(CustomerSimilarityAnalysis.version_mark == version_mark)

        res = self.session.execute(st).scalars()
        return res.all()

    @menage_db_method(CommitMode.FLUSH)
    def update_state_all_comments_available(self, customer: Customer, new_state: bool):
        customer.is_all_comments_available = new_state
        self.session.add(customer)

    @menage_db_method(CommitMode.FLUSH)
    def update_similarity_values_customer_similarity_analysis(self,
                                                              customer_similarity_analysis: CustomerSimilarityAnalysis,
                                                              similarity_value_reviews: Optional[float],
                                                              similarity_value_comments: Optional[float]):
        if similarity_value_reviews is not None:
            customer_similarity_analysis.similarity_reviews_value = similarity_value_reviews
        if similarity_value_comments is not None:
            customer_similarity_analysis.similarity_comments_value = similarity_value_comments
        self.session.add(customer_similarity_analysis)

    @menage_db_method(CommitMode.FLUSH)
    def update_state_all_reviews_available(self, customer: Customer, new_state: bool):
        customer.is_all_reviews_available = new_state
        self.session.add(customer)
