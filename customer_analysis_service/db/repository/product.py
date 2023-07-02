from sqlmodel import select, Session

from customer_analysis_service.db.models.product import Product


class ProductRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def add_product(self, review: Product):
        self.session.add(review)
        self.session.commit()

    def get_product(self, name_id: str) -> Product:
        return self.session.exec(select(Product).where(Product.name_id == name_id)).first()

    def get_all_products(self) -> list[Product]:
        return self.session.exec(select(Product))

    def update_state_all_customers_information_available_for_product(self, product: Product, new_state: bool):
        product.is_all_customers_information_available_for_product = new_state
        self.session.add(product)
        self.session.commit()
