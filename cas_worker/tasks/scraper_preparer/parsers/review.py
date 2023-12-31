import re
from datetime import datetime
from urllib.parse import unquote

from scrapy import Selector, Request
from scrapy.http import Response

from cas_worker.tasks.scraper_preparer.items import ReviewItem
from cas_worker.tasks.scraper_preparer.parsers import ProductParser, CustomerParser
from cas_worker.tasks.scraper_preparer.spiders.utils.error import handle_http_errors


class ReviewParser:
    @classmethod
    @handle_http_errors
    def parse_review(cls, response: Response, **kwargs):
        for item in ReviewParser.extract_review_content_data(Selector(response)):
            yield item

    @classmethod
    def extract_review_content_data(cls, selector: Selector):
        r_href: str = selector.css('a.review-comments ::attr(href)').get()
        match = re.search(r'\d+', r_href)
        r_id: int = int(match.group())

        ru_categories_str = selector.css('div.breadcrumbs a')
        count_category = min(len(ru_categories_str), 5)  # 1 more, since the category is the reviews section of the site

        review = ReviewItem()
        review['id'] = r_id
        for i in range(1, count_category):
            review[f'ru_category_{i}'] = ru_categories_str[i].css('::text').get()
            review[f'href_category_{i}'] = unquote(ru_categories_str[i].css('::attr(href)').get())
        if count_category < 5:
            review[f'ru_category_{4}'] = None
            review[f'href_category_{4}'] = None

        evaluated_product_name_id = selector.css('a.product-name ::attr(href)').get().split('/')[2]
        yield Request(f'https://otzovik.com/reviews/{evaluated_product_name_id}/info/', callback=ProductParser.parse_product)
        # all customer reviews may contain products that are not yet in the database

        review['evaluated_product_name_id'] = evaluated_product_name_id

        customer_name_id = selector.css('a.user-login span ::text').get().replace(' ', '+')
        yield Request(f'https://otzovik.com/profile/{customer_name_id}', callback=CustomerParser.parse_customer)
        # the review may be a customer that has not yet been added to the database

        review['customer_name_id'] = customer_name_id

        review['count_user_recommend_review'] = int(
            selector.xpath('//span[@class="review-btn review-yes"]/text()').get())
        review['count_comments_review'] = int(selector.css('a.review-comments ::text').get())
        review['date_review'] = datetime.strptime(selector.css('span.review-postdate span.tooltip-right ::text').get(),
                                                  '%d.%m.%Y').date()
        review['advantages'] = selector.css('div.review-plus ::text').get()
        review['disadvantages'] = selector.css('div.review-minus ::text').get()
        review['text_review'] = re.sub(r'<.*?>', '', selector.css('div.review-body').get())\
            .replace('(adsbygoogle = window.adsbygoogle || []).push({});', '')

        t_body = selector.css('table.product-props tbody')[1].css('tr')
        params_dict = {item.css('td ::text')[0].get(): item.css('td')[1] for item in t_body}

        review['general_impression'] = params_dict.get('Общее впечатление:').css('i ::text').get()
        review['star_rating'] = float(params_dict.get('Моя оценка:')
                                      .css('div.product-rating ::attr(title)').get().split(': ')[1])
        review['recommend_friends'] = params_dict.get('Рекомендую друзьям:').css('::text').get() == 'ДА'

        yield review
