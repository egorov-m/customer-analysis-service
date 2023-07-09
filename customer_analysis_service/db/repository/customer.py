from sqlmodel import select, Session

from customer_analysis_service.db.models.customer import Customer, CustomerSimilarityAnalysis


class CustomerRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def add_customer(self, customer: Customer):
        self.session.add(customer)
        self.session.commit()

    def add_product_sentiment_analysis(self, customer_sentiment_analysis: CustomerSimilarityAnalysis):
        self.session.add(customer_sentiment_analysis)
        self.session.commit()

    def get_customer(self, name_id: str) -> Customer:
        return self.session.exec(select(Customer).where(Customer.name_id == name_id)).first()

    def get_all_customers(self) -> list[Customer]:
        return self.session.exec(select(Customer)).all()

    def get_customers_similarity_analysis(self, customer_name_id: str, version_mark: str = None):
        query = select(CustomerSimilarityAnalysis).where(CustomerSimilarityAnalysis.customer_name_id == customer_name_id)
        if version_mark is not None:
            query.where(CustomerSimilarityAnalysis.version_mark == version_mark)

        return self.session.exec(query).all()

    def update_state_all_comments_available(self, customer: Customer, new_state: bool):
        customer.is_all_comments_available = new_state
        self.session.add(customer)
        self.session.commit()

    def update_similarity_values_customer_similarity_analysis(self, customer_similarity_analysis: CustomerSimilarityAnalysis,
                                                              similarity_value_reviews: float,
                                                              similarity_value_comments: float):
        customer_similarity_analysis.similarity_reviews_value = similarity_value_reviews
        customer_similarity_analysis.similarity_comments_value = similarity_value_comments
        self.session.add(customer_similarity_analysis)
        self.session.commit()

    def update_state_all_reviews_available(self, customer: Customer, new_state: bool):
        customer.is_all_reviews_available = new_state
        self.session.add(customer)
        self.session.commit()
