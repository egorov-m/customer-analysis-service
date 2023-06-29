from urllib.parse import urlparse

from scrapy import Spider
from scrapy.http import Response


def spider_pagination(spider: Spider, response: Response):
    next_page = response.css('div.pager a.next ::attr(href)').get()
    if next_page is not None:
        parsed_response_url = urlparse(response.url)
        next_page_url = f'{parsed_response_url.scheme}://{parsed_response_url.netloc}{next_page}'
        yield response.follow(next_page_url, callback=spider.parse)
