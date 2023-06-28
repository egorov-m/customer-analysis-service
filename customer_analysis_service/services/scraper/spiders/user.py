import re
import logging
from datetime import datetime
from urllib.parse import urlparse

from scrapy import Spider, Request
from scrapy.http import Response

from customer_analysis_service.services.scraper.items import Customer, InfoToFindAllCustomers


class CustomerSpider(Spider):
    name = 'customer'

    def __init__(self, customer_name_id: int, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = [f'https://otzovik.com/profile/{customer_name_id}']
        self.customer_name_id = customer_name_id

    def start_requests(self):
        url = self.start_urls[0]
        yield Request(url, callback=self.parse)

    @classmethod
    def _table_to_dict(cls, table):
        return {item.css('td ::text')[0].get(): item.css('td ::text')[1].get() for item in table}

    def parse(self, response: Response, **kwargs):
        self.log(response.url)
        name_id = self.customer_name_id
        reputation = int(
            response.css('div.content div.content-left div.glory-box div.karma div[class^="karma"] ::text').get())
        table_selectors = 'div.content div.content-right div.columns'

        table_1 = response.css(f'{table_selectors} table.table_1 tr')
        table_2 = response.css(f'{table_selectors} table.table_2 tr')
        table_1_dict = self._table_to_dict(table_1)
        table_2_dict = self._table_to_dict(table_2)

        country = table_1_dict.get('Страна:')
        city = table_1_dict.get('Город:')
        profession = table_1_dict.get('Профессия:')

        reg_date_str: str = table_1_dict.get('Регистрация:')
        month_dict = {'янв': '01', 'фев': '02', 'мар': '03', 'апр': '04', 'май': '05', 'июн': '06',
                      'июл': '07', 'авг': '08', 'сен': '09', 'окт': '10', 'ноя': '11', 'дек': '12'}
        for key, value in month_dict.items():
            reg_date_str = reg_date_str.replace(key, value)
        reg_date = datetime.strptime(reg_date_str, '%d %m %Y').date()
        count_subscribers = int(table_2_dict.get('Подписчиков:'))

        customer = Customer()
        customer['name_id'] = name_id
        customer['reputation'] = reputation
        customer['country'] = country
        customer['city'] = city
        customer['profession'] = profession
        customer['reg_date'] = reg_date
        customer['count_subscribers'] = count_subscribers
        # customer['last_activity_date'] = last_activity_date

        yield customer


class AllUserReviewsForProductSpider(Spider):
    name = 'all_user_reviews_for_product'

    def __init__(self, product_title_id: str, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = [f'https://otzovik.com/reviews/{product_title_id}/']

    def start_requests(self):
        url = self.start_urls[0]
        yield Request(url, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        self.log(response.url)

        reviews = response.css('div.review-list-chunk div.item')

        info_to_find_all_customers_item = InfoToFindAllCustomers()
        for review in reviews:
            customer_name_id: str = review.css(
                'div.item .item-left div.user-info div.login-line a.user-login span::text').get()
            review_path: str = review.css('div.item .item-right div.review-bar a.review-read-link ::attr(href)').get()
            if customer_name_id is not None:
                info_to_find_all_customers_item['customer_name_id'] = customer_name_id.replace(' ', '+')
                if review_path is not None:
                    match = re.search(r"\d+", review_path)
                    if match:
                        review_id: int = int(match.group())
                        info_to_find_all_customers_item['review_id'] = review_id
                        yield info_to_find_all_customers_item
                    else:
                        self.log('Error format review_id!', level=logging.ERROR)
                else:
                    self.log('Error parse review_id!', level=logging.ERROR)
            else:
                self.log('Error parse customer_name_id!', level=logging.ERROR)

        next_page = response.css('div.pager a.next ::attr(href)').get()
        if next_page is not None:
            parsed_response_url = urlparse(response.url)
            next_page_url = f'{parsed_response_url.scheme}://{parsed_response_url.netloc}{next_page}'
            yield response.follow(next_page_url, callback=self.parse)
