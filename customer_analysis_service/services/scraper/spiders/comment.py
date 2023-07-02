import re
from datetime import datetime

from scrapy import Spider, Request
from scrapy.http import Response

from customer_analysis_service.services.scraper.items import CommentItem
from customer_analysis_service.services.scraper.spiders.utils.pagination import spider_pagination


class CommentsCustomerSpider(Spider):
    name = 'comments_customer_spider'

    def __init__(self, customer_name_ids: list[int], **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://otzovik.com/?author_comments={customer_name_id}' for customer_name_id in customer_name_ids]
        customer_name_ids.clear()

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        customer_comments = response.css('div.author-comments')
        r_links = customer_comments.css('div.rlink')
        comment_treads = customer_comments.css('div.comment-thread')
        comment = CommentItem()
        comment['customer_name_id'] = comment_treads.css('div.comment div.comment-right a.user-login ::text').get()

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
