from scrapy import Spider, Request
from scrapy.http import Response


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
