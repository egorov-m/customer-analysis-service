from urllib.parse import urlparse

from scrapy import Spider, Request
from scrapy.http import Response, Headers


class CategoriesSpider(Spider):
    name = 'categories'

    def __init__(self, href_category_1: str, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = [f'https://otzovik.com{href_category_1}']

    def start_requests(self):
        url = self.start_urls[0]
        yield Request(url, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        self.log(response.url)
        categories = response.css('div.sitemap ul li.section ul li h3 a')
        for category in categories:
            yield {
                'ru_category_2': category.css('span ::text').get(),
                'href_category_2': category.css('::attr(href)').get()
            }


class ProductNameIdCategorySpider(Spider):
    name = 'product_name_id_category'

    def __init__(self, href_category: str, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = [f'https://otzovik.com/{href_category}']

    def start_requests(self):
        url = self.start_urls[0]
        yield Request(url, callback=self.parse, headers=Headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:114.0) Gecko/20100101 Firefox/114.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Sec-GPC": "1",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Referrer": "https://otzovik.com/show_filter.php?cat_id=86&f[b]=Rombica&capt4a=5781687991586909",
                "DNT": 1,
                'Connection': 'keep-alive',
            }), cookies={
                'ROBINBOBIN': 'e2fe04cfee80c6c08d15d1506a',
                'ssid': '2566477564',
                'refreg': '1687981090~https%3A%2F%2Fotzovik.com%2Freviews%2Fbesprovodnie_igrovie_naushniki_sony_inzone_h7%2F%3F%26capt4a%3D3201687981067127',
            })

    def parse(self, response: Response, **kwargs):
        self.log(response.url)
        product_list = response.css('div.product-list table tr.item td div.product-photo a ::attr(href)')
        for product in product_list:
            yield {'product_name_id': product.get().split('/')[2]}

        next_page = response.css('div.pager a.next ::attr(href)').get()
        if next_page is not None:
            parsed_response_url = urlparse(response.url)
            next_page_url = f'{parsed_response_url.scheme}://{parsed_response_url.netloc}{next_page}'
            yield response.follow(next_page_url, callback=self.parse, headers=Headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:114.0) Gecko/20100101 Firefox/114.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Sec-GPC": "1",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Referrer": "https://otzovik.com/show_filter.php?cat_id=86&f[b]=Rombica&capt4a=5781687991586909",
                "DNT": 1,
                'Connection': 'keep-alive',
            }), cookies={
                'ROBINBOBIN': 'e2fe04cfee80c6c08d15d1506a',
                'ssid': '2566477564',
                'refreg': '1687981090~https%3A%2F%2Fotzovik.com%2Freviews%2Fbesprovodnie_igrovie_naushniki_sony_inzone_h7%2F%3F%26capt4a%3D3201687981067127',
            })


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
