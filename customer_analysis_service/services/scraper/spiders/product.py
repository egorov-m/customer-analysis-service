from scrapy import Spider, Request
from scrapy.http import Response

from customer_analysis_service.services.scraper.items import Product
from customer_analysis_service.services.scraper.spiders.utils.pagination import spider_pagination


class ProductSpider(Spider):
    name = 'product'

    def __init__(self, product_name_id: int, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = [f'https://otzovik.com/reviews/{product_name_id}/info/']
        self.product_name_id = product_name_id

    def start_requests(self):
        url = self.start_urls[0]
        yield Request(url, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        fullname = response.css('a.product-name span ::text').get()
        image_url = f'https:{response.css("div.product-photo img ::attr(src)").get()}'
        product_info = response.css('div.product-info')

        title_block: str = str(product_info.css(".title_block ::text").get()).replace('None', '')
        text_block: str = str(product_info.css(".text_block ::text").getall()).replace('None', '').strip()
        props_block: str = ''
        for item in product_info.css('table.product-props tr'):
            key = item.css('td ::text')[0].get()
            value = item.css('td ::text')[1].get()
            props_block += f'{key}: {value}\n'

        description: str = title_block + text_block + '\n' + props_block

        product = Product()
        product['name_id'] = self.product_name_id
        product['fullname'] = fullname
        product['image_url'] = image_url
        product['description'] = description

        yield product


class ProductNameIdCategorySpider(Spider):
    name = 'product_name_id_category'

    def __init__(self, href_category: str, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = [f'https://otzovik.com{href_category}']

    def start_requests(self):
        url = self.start_urls[0]
        yield Request(url, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        self.log(response.url)
        product_list = response.css('div.product-list table tr.item td div.product-photo a ::attr(href)')
        for product in product_list:
            yield {'product_name_id': product.get().split('/')[2]}

        for item in spider_pagination(self, response):
            yield item


class ProductNameIdFilters(ProductNameIdCategorySpider):
    name = 'product_name_id_filters'
    # Perhaps add more flexibility when working with filters

    def __init__(self, filter_args: int, name=None, **kwargs):
        """
        :param filter_args: from the address line, example: cat_id={id}&f[b]={brand_name}
        :param name:
        :param kwargs:
        """
        super().__init__('', name, **kwargs)
        self.start_urls = [f'https://otzovik.com/show_filter.php?{filter_args}']
