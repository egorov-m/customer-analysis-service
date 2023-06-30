import re
import logging
from datetime import datetime

from scrapy import Spider, Request
from scrapy.http import Response

from customer_analysis_service.services.scraper.items import CustomerItem, InfoToFindAllCustomers
from customer_analysis_service.services.scraper.spiders.utils.pagination import spider_pagination


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

        country_str = table_1_dict.get('Страна:')
        country = country_str if country_str is not None and country_str != '<Нет>' else None
        city_str = table_1_dict.get('Город:')
        city = city_str if city_str is not None and city_str != '<Нет>' else None
        profession = table_1_dict.get('Профессия:')

        reg_date_str: str = table_1_dict.get('Регистрация:')
        month_dict = {'янв': '01', 'фев': '02', 'мар': '03', 'апр': '04', 'май': '05', 'июн': '06',
                      'июл': '07', 'авг': '08', 'сен': '09', 'окт': '10', 'ноя': '11', 'дек': '12'}
        for key, value in month_dict.items():
            reg_date_str = reg_date_str.replace(key, value)
        reg_date = datetime.strptime(reg_date_str, '%d %m %Y').date()
        count_subscribers = int(table_2_dict.get('Подписчиков:'))

        customer = CustomerItem()
        customer['name_id'] = name_id
        customer['reputation'] = reputation
        customer['country'] = country
        customer['city'] = city
        customer['profession'] = profession
        customer['reg_date'] = reg_date
        customer['count_subscribers'] = count_subscribers
        # customer['last_activity_date'] = last_activity_date

        yield customer


class AllCustomersReviewsForProductSpider(Spider):
    name = 'all_customers_reviews_for_product'

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
                    self.log('Error parse_products review_id!', level=logging.ERROR)
            else:
                self.log('Error parse_products customer_name_id!', level=logging.ERROR)

        for item in spider_pagination(self, response):
            yield item


class CustomerIdCommentingOnReviewSpider(Spider):
    name = 'customer_commenting_on_review'

    def __init__(self, review_id: int, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = [f'https://otzovik.com/review_{review_id}.html']

    def start_requests(self):
        url = self.start_urls[0]
        yield Request(url, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        self.log(response.url)

        comment_treads = response.css('#comments-container div.comment-thread')
        set_without_repetitions = set()
        for comment_item in self.recursively_bypass_comments(comment_treads):
            # customers can give multiple comments, only customers without repetition are needed
            if comment_item not in set_without_repetitions:
                set_without_repetitions.add(comment_item)
                yield {'customer_name_id': comment_item}

    def recursively_bypass_comments(self, comment_treads: list):
        for comment_tread in comment_treads:
            comment = comment_tread.css('div.comment')[0].css('div.comment-right')
            yield comment.css('a ::text').get().replace(' ', '+')
            comment_treads_child = comment_tread.css('div.comment-thread')
            self.recursively_bypass_comments(comment_treads_child)
