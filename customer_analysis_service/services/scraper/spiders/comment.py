import re
from datetime import datetime

from scrapy import Spider, Request
from scrapy.http import Response

from customer_analysis_service.services.scraper.items import Comment
from customer_analysis_service.services.scraper.spiders.utils.pagination import spider_pagination


class CommentsCustomerSpider(Spider):
    name = 'comments_customer'

    def __init__(self, customer_name_id: int, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = [f'https://otzovik.com/?author_comments={customer_name_id}']
        self.customer_name_id = customer_name_id

    def start_requests(self):
        url = self.start_urls[0]
        yield Request(url, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        self.log(response.url)

        customer_comments = response.css('div.author-comments')
        r_links = customer_comments.css('div.rlink')
        comment_treads = customer_comments.css('div.comment-thread')
        comment = Comment()
        comment['customer_name_id'] = self.customer_name_id

        for r_link, comment_tread in zip(r_links, comment_treads):
            review_id_href: str = r_link.css('a ::attr(href)').get()
            if review_id_href is None:
                # Review is temporarily unavailable on the site, do not take it into account
                break
            comment['review_id'] = re.search(r'review_(\d+)', review_id_href).group(1)
            comment_block = comment_tread.css('div.comment')[0].css('div.comment-right')
            comment['reg_datetime'] = datetime.strptime(comment_block.css('div.comment-postdate ::text').get(), '%d.%m.%Y %H:%M:%S')
            comment['text_comment'] = comment_block.css('div.comment-body ::text').getall()
            yield comment

        for item in spider_pagination(self, response):
            yield item
