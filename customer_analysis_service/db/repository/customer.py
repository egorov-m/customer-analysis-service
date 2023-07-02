from sqlmodel import select, Session

from customer_analysis_service.db.models.customer import Customer


class CustomerRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def add_customer(self, customer: Customer):
        self.session.add(customer)
        self.session.commit()

    def get_customer(self, name_id: str) -> Customer:
        return self.session.exec(select(Customer).where(Customer.name_id == name_id))

    def get_all_customers(self) -> list[Customer]:
        return self.session.exec(select(Customer))

    def update_state_all_comments_available(self, customer: Customer, new_state: bool):
        customer.is_all_comments_available = new_state
        self.session.add(customer)
        self.session.commit()

    def update_state_all_reviews_available(self, customer: Customer, new_state: bool):
        customer.is_all_reviews_available = new_state
        self.session.add(customer)
        self.session.commit()
