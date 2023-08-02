import re
from datetime import datetime

from scrapy import Spider, Request
from scrapy.http import Response

from cas_worker.services.scraper.items import CommentItem
from cas_worker.services.scraper.parsers import ReviewParser
from cas_worker.services.scraper.spiders.utils.error import handle_http_errors
from cas_worker.services.scraper.spiders.utils.pagination import spider_pagination


class CommentsCustomerSpider(Spider):
    name = 'comments_customer_spider'

    def __init__(self, customer_name_ids: str, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://otzovik.com/?author_comments={customer_name_id}' for customer_name_id in customer_name_ids.split(' ')]
        self.handle_httpstatus_list = [507]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse)

    @handle_http_errors
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
            review_id = re.search(r'review_(\d+)', review_id_href).group(1)
            yield Request(f'https://otzovik.com/review_{review_id}.html', callback=ReviewParser.parse_review)
            # all customer comments may contain reviews that are not yet in the database

            comment['review_id'] = review_id
            comment_block = comment_tread.css('div.comment')[0].css('div.comment-right')
            comment['reg_datetime'] = datetime.strptime(comment_block.css('div.comment-postdate ::text').get(), '%d.%m.%Y %H:%M:%S')
            comment['text_comment'] = comment_block.css('div.comment-body ::text').getall()
            yield comment

        for item in spider_pagination(self, response):
            yield item
