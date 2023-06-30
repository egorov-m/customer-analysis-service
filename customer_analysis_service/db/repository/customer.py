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
        return self.session.execute(select(Customer).where(Customer.name_id == name_id))

    def get_all_customers(self) -> list[Customer]:
        return self.session.execute(select(Customer))
