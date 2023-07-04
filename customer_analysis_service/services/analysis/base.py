from customer_analysis_service.db import Database


class BaseServices:
    def __init__(self, database: Database):
        self.database = database
