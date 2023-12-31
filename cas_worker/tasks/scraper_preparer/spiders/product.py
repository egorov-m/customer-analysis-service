from scrapy import Spider, Request
from scrapy.http import Response

from cas_worker.tasks.scraper_preparer.parsers import ProductParser
from cas_worker.tasks.scraper_preparer.spiders.utils.error import handle_http_errors
from cas_worker.tasks.scraper_preparer.spiders.utils.pagination import spider_pagination


class ProductSpider(Spider):
    """
    Allows you to get information about the product.
    Starting from a page with a list of subcategories or a list of category products.
    """
    name = 'product_spider'

    def __init__(self, href_product_path: str, max_count_items: int = 5, **kwargs):
        """
        :param href_product_path:
               format example:
                   search_product: /?search_text={input_text}
                   category_1:     /category_1/
                   category_2:     /category_1/category_2/
                   category_3:     /category_1/category_2/category_3/
                   category_4:     /show_filter.php?cat_id={cat_id}&f[b]={brand_name}
        :param name:
        :param kwargs:
        """

        super().__init__(**kwargs)
        self.start_urls = [f'https://otzovik.com{href_product_path}']
        self.href_category = href_product_path
        self.handle_httpstatus_list = [507]
        self.max_count_items = int(max_count_items)
        self.count_items = 0

    def start_requests(self):
        url = self.start_urls[0]

        if len(self.href_category.split('/')) == 3 and not self.href_category.__contains__('?search_text'):
            # category_1 - list of more nested categories
            yield Request(url, callback=self.parse_categories)
        else:
            # other categories - list of products
            yield Request(url, callback=self.parse)

    @handle_http_errors
    def parse(self, response: Response, **kwargs):
        product_list = response.css('div.product-list table tr.item td div.product-photo a ::attr(href)')
        for product in product_list:
            if self.max_count_items is not None and self.count_items >= self.max_count_items:
                return
            yield Request(f'https://otzovik.com/reviews/{product.get().split("/")[2]}/info/', callback=ProductParser.parse_product)
            self.count_items += 1

        for item in spider_pagination(self, response):
            yield item

    @handle_http_errors
    def parse_categories(self, response: Response, **kwargs):
        self.log(response.url)
        categories = response.css('div.sitemap ul li.section ul li h3 a')
        for category in categories:
            yield Request(f'https://otzovik.com{category.css("::attr(href)").get()}', callback=self.parse)
