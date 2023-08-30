from cas_worker.tasks.scraper.items import CustomerItem
from cas_worker.tasks.scraper.spiders import CustomerSpider, ReviewsCustomerSpider, CommentsCustomerSpider
from cas_worker.tasks.scraper.tasks.base import BaseScraperTask
from config import WorkerTasks


class ProductsDataScraperTask(BaseScraperTask):
    def __init__(self):
        super().__init__()
        self.name = self.name = WorkerTasks.products_data

    def run(self, product_name_id: str):
        self.logger.info(f'The parsing of the product has started: {product_name_id}!')

        self.start_sub_process_spider(CustomerSpider, product_name_ids=[product_name_id])

        customers: list[CustomerItem] = self.extract_from_buffer()

        self.start_sub_process_spider(ReviewsCustomerSpider, customer_name_ids=[item['name_id'] for item in customers])

        self.start_sub_process_spider(CommentsCustomerSpider, customer_name_ids=[item['name_id'] for item in customers])

        self.logger.info(f'Product parsing: {product_name_id} completed!')
