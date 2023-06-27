import re
from datetime import datetime

from scrapy import Spider, Request
from scrapy.http import Response

from customer_analysis_service.services.scraper.items import Review


class ReviewSpider(Spider):
    name = 'review'

    def __init__(self, review_id: int, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = [f'https://otzovik.com/review_{review_id}.html']
        self.review_id = review_id

    def start_requests(self):
        url = self.start_urls[0]
        yield Request(url, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        self.log(response.url)

        r_id: int = self.review_id

        ru_categories_str = response.css('div.breadcrumbs a')
        count_category = min(len(ru_categories_str), 5)  # 1 more, since the category is the reviews section of the site

        review = Review()
        review['id'] = r_id
        for i in range(1, count_category):
            review[f'ru_category_{i}'] = ru_categories_str[i].css('::text').get()
            review[f'en_category_{i}'] = ru_categories_str[i].css('::attr(href)').get().split('/')[i]

        review['evaluated_product_name_id'] = response.css('a.product-name ::attr(href)').get().split('/')[2]
        review['customer_name_id'] = response.css('a.user-login span ::text').get().replace(' ', '+')
        review['count_user_recommend_review'] = int(response.xpath('//span[@class="review-btn review-yes"]/text()').get())
        review['count_comments_review'] = int(response.css('a.review-comments ::text').get())
        review['date_review'] = datetime.strptime(response.css('span.review-postdate span.tooltip-right ::text').get(),
                                                  '%d.%m.%Y').date()
        review['advantages'] = response.css('div.review-plus ::text').get()
        review['disadvantages'] = response.css('div.review-minus ::text').get()
        review['text_review'] = re.sub(r'<.*?>', '', response.css('div.review-body').get())
        review['year_service'] = int(response.css('table.product-props tr td ::text')[1].get())
        review['general_impression'] = response.css('table.product-props tr')[1].css('td i ::text').get()
        review['star_rating'] = float(response.css('table.product-props tr')[2]
                                      .css('td div.product-rating ::attr(title)').get().split(': ')[1])
        review['recommend_friends'] = response.css('table.product-props tr')[3].css('td.recommend-ratio ::text').get() == 'ДА'

        yield review
