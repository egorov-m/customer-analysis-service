from scrapy import Spider, Request


class ReviewSpider(Spider):
    name = 'review'

    def start_requests(self):
        url = ''
        yield Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        pass
