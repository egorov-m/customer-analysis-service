import logging
from urllib.parse import urlparse

from scrapy import Spider, Request
from scrapy.http import Response

from customer_analysis_service.services.scraper.items import Customer


class UserSpider(Spider):
    name = 'user'

    def start_requests(self):
        url = ''
        yield Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        pass


class AllUsersForProductSpider(Spider):
    name = 'all_users_for_product'

    def __init__(self, product_title_id: str, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = [f'https://otzovik.com/reviews/{product_title_id}/']

    def start_requests(self):
        url = self.start_urls[0]
        yield Request(url, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        self.log(response.url)

        reviews = response.css('div.review-list-chunk div.item')

        user_item = Customer()
        for review in reviews:
            username: str = review.css('div.item .item-left div.user-info div.login-line a.user-login span::text').get()
            if username is not None:
                user_item['name_id'] = username.replace(' ', '+')
                yield user_item
            else:
                self.log('Error parse username!', level=logging.ERROR)

        next_page = response.css('div.pager a.next ::attr(href)').get()
        if next_page is not None:
            parsed_response_url = urlparse(response.url)
            next_page_url = f'{parsed_response_url.scheme}://{parsed_response_url.netloc}{next_page}'
            yield response.follow(next_page_url, callback=self.parse)
