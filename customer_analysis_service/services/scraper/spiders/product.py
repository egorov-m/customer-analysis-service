from scrapy import Spider, Request, Selector
from scrapy.http import Response

from customer_analysis_service.services.scraper.parsers.product import ProductParser
from customer_analysis_service.services.scraper.spiders.utils.pagination import spider_pagination


def parse_product(response: Response):
    return ProductParser.extract_product_info(Selector(response))


class ProductSpider(Spider):
    """
    Allows you to get information about the product.
    Starting from a page with a list of subcategories or a list of category products.
    """
    name = 'product_spider'

    def __init__(self, href_product_path: str, **kwargs):
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

    def start_requests(self):
        url = self.start_urls[0]

        if len(self.href_category.split('/')) == 3 and not self.href_category.__contains__('?search_text'):
            # category_1 - list of more nested categories
            yield Request(url, callback=self.parse_categories)
        else:
            # other categories - list of products
            yield Request(url, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        product_list = response.css('div.product-list table tr.item td div.product-photo a ::attr(href)')
        for product in product_list:
            yield Request(f'https://otzovik.com/reviews/{product.get().split("/")[2]}/info/', callback=parse_product)

        for item in spider_pagination(self, response):
            yield item

    def parse_categories(self, response: Response):
        self.log(response.url)
        categories = response.css('div.sitemap ul li.section ul li h3 a')
        for category in categories:
            yield Request(f'https://otzovik.com{category.css("::attr(href)").get()}', callback=self.parse)
