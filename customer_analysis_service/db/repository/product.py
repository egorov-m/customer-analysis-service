from sqlmodel import select, Session

from customer_analysis_service.db.models.product import Product, ProductSimilarityAnalysis


class ProductRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def add_product(self, review: Product):
        self.session.add(review)
        self.session.commit()

    def add_product_sentiment_analysis(self, product_sentiment_analysis: ProductSimilarityAnalysis):
        self.session.add(product_sentiment_analysis)
        self.session.commit()

    def get_product(self, name_id: str) -> Product:
        return self.session.exec(select(Product).where(Product.name_id == name_id)).first()

    def get_all_products(self) -> list[Product]:
        return self.session.exec(select(Product)).all()

    def get_products_similarity_analysis(self, product_name_id: str, version_mark: str = None):
        query = select(ProductSimilarityAnalysis).where(ProductSimilarityAnalysis.product_name_id == product_name_id)
        if version_mark is not None:
            query.where(ProductSimilarityAnalysis.version_mark == version_mark)

        return self.session.exec(query).all()

    def update_similarity_values_product_similarity_analysis(self, product_similarity_analysis: ProductSimilarityAnalysis,
                                                             similarity_value_reviews: float,
                                                             similarity_value_comments: float):
        product_similarity_analysis.similarity_reviews_value = similarity_value_reviews
        product_similarity_analysis.similarity_comments_value = similarity_value_comments
        self.session.add(product_similarity_analysis)
        self.session.commit()

    def update_state_all_customers_information_available_for_product(self, product: Product, new_state: bool):
        product.is_all_customers_information_available_for_product = new_state
        self.session.add(product)
        self.session.commit()
