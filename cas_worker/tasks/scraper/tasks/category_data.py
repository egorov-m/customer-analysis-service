from cas_worker.tasks.scraper.items import ProductItem, CustomerItem
from cas_worker.tasks.scraper.spiders import (
    ProductSpider,
    CustomerSpider,
    ReviewsCustomerSpider,
    CommentsCustomerSpider
)
from cas_worker.tasks.scraper.tasks.base import BaseScraperTask
from config import WorkerTasks


class CategoryDataScraperTask(BaseScraperTask):
    def __init__(self):
        super().__init__()
        self.name = self.name = WorkerTasks.category_data

    def run(self, href_product_path: str):
        self.logger.info(f'Starting scraping for a category: {href_product_path}')

        products: list[ProductItem] = self.get_list_item(self.start_sub_process_spider(ProductSpider,
                                                                                       href_product_path=href_product_path))

        customers: list[CustomerItem] = self.get_list_item(self.start_sub_process_spider(CustomerSpider,
                                                                                         product_name_ids=[item['name_id'] for item in products]))

        self.start_sub_process_spider(ReviewsCustomerSpider, customer_name_ids=[item['name_id'] for item in customers])

        self.start_sub_process_spider(CommentsCustomerSpider, customer_name_ids=[item['name_id'] for item in customers])

        self.logger.info(f'Category parsing: {href_product_path} completed!')
