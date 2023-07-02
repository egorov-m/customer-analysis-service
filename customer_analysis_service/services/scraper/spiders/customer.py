import re
import logging

from scrapy import Spider, Request
from scrapy.selector import Selector
from scrapy.http import Response

from customer_analysis_service.services.scraper.parsers.customer import CustomerParser
from customer_analysis_service.services.scraper.spiders.utils.pagination import spider_pagination


def parse_customer(response: Response):
    return CustomerParser.extract_customer_profile_data(Selector(response))


class CustomerSpider(Spider):
    """
    Allows you to get information about all customers of a product
    who have written reviews or commented on reviews.
    """
    name = 'customer_spider'

    def __init__(self, product_name_ids: list[str], **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://otzovik.com/reviews/{product_name_id}/' for product_name_id in product_name_ids]
        product_name_ids.clear()

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        reviews = response.css('div.review-list-chunk div.item')
        set_reviewing_customer_without_repetitions = set()

        for review in reviews:
            customer_name_id: str = review.css(
                'div.item .item-left div.user-info div.login-line a.user-login span::text').get()
            review_path: str = review.css('div.item .item-right div.review-bar a.review-read-link ::attr(href)').get()
            if customer_name_id is not None and customer_name_id is not set_reviewing_customer_without_repetitions:
                set_reviewing_customer_without_repetitions.add(customer_name_id)
                customer_name_id = customer_name_id.replace(' ', '+')
                yield Request(f'https://otzovik.com/profile/{customer_name_id}', callback=parse_customer)

                if review_path is not None:
                    match = re.search(r'\d+', review_path)
                    if match:
                        review_id: int = int(match.group())
                        yield Request(f'https://otzovik.com/review_{review_id}.html', callback=self.parse_commenting_customers)
                    else:
                        self.log('Error format review_id!', level=logging.ERROR)
                else:
                    self.log('Error parse review_id!', level=logging.ERROR)
            else:
                self.log('Error parse customer_name_id!', level=logging.ERROR)

        for item in spider_pagination(self, response):
            yield item

    def parse_commenting_customers(self, response: Response):
        comment_treads = response.css('#comments-container div.comment-thread')
        set_without_repetitions = set()
        for customer_name_id in self.recursively_bypass_comments(comment_treads):
            # customers can give multiple comments, only customers without repetition are needed
            if customer_name_id not in set_without_repetitions:
                set_without_repetitions.add(customer_name_id)
                yield Request(f'https://otzovik.com/profile/{customer_name_id}', callback=parse_customer)

    def recursively_bypass_comments(self, comment_treads: list):
        for comment_tread in comment_treads:
            comment = comment_tread.css('div.comment')[0].css('div.comment-right')
            yield comment.css('a ::text').get().replace(' ', '+')
            comment_treads_child = comment_tread.css('div.comment-thread')
            self.recursively_bypass_comments(comment_treads_child)
