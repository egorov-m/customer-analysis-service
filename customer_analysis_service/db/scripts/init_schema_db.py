if __name__ == '__main__':

    from sqlmodel import SQLModel

    from customer_analysis_service.config import Config
    from customer_analysis_service.db.database import create_engine
    from customer_analysis_service.db.models.customer import Customer, CustomerGeneralAnalysis
    from customer_analysis_service.db.models.review import Review
    from customer_analysis_service.db.models.product import Product
    from customer_analysis_service.db.models.comment import Comment

    cas_config: Config = Config.load_config()
    async_engine = create_engine(url=cas_config.dbPostgres.get_url())
    SQLModel.metadata.create_all(async_engine)
