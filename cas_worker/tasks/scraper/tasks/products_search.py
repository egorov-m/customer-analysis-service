from cas_worker.tasks.scraper.spiders import ProductSpider
from cas_worker.tasks.scraper.tasks.base import BaseScraperTask
from config import WorkerTasks


class ProductsSearchScraperTask(BaseScraperTask):
    def __init__(self):
        super().__init__()
        self.name = self.name = WorkerTasks.products_search

    def run(self, search_input: str, max_count_items: int = 5) -> list[dict]:
        href_search_path: str = f'/?search_text={search_input}'
        self.logger.info('The search for products by search query begins!')

        self.start_sub_process_spider(ProductSpider,
                                      href_product_path=href_search_path,
                                      max_count_items=max_count_items)

        self.logger.info('Products found!')

        return self.extract_from_buffer()
