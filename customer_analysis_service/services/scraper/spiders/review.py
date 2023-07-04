import logging
import re

from scrapy import Spider, Request
from scrapy.http import Response

from customer_analysis_service.services.scraper.parsers import ReviewParser
from customer_analysis_service.services.scraper.spiders.utils.error import handle_http_errors
from customer_analysis_service.services.scraper.spiders.utils.pagination import spider_pagination


class ReviewsCustomerSpider(Spider):
    name = 'reviews_customer_spider'

    def __init__(self, customer_name_ids: list[str], **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://otzovik.com/?search_text={customer_name_id}&us=1' for customer_name_id in customer_name_ids]
        self.handle_httpstatus_list = [507]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse)

    @handle_http_errors
    def parse(self, response: Response, **kwargs):
        reviews_path = response.css(
            'div.review-list-chunk div.item div.item-right div.review-bar a.review-read-link ::attr(href)')
        for review_path in reviews_path:
            href = review_path.get()
            match = re.search(r'\d+', href)
            if match:
                review_id: int = int(match.group())
                yield Request(f'https://otzovik.com/review_{review_id}.html', callback=ReviewParser.parse_review)
            else:
                self.log('Error format review_id!', level=logging.ERROR)

        for item in spider_pagination(self, response):
            yield item
