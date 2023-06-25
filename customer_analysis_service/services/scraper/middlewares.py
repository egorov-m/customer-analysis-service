# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from random import randint

from scrapy import signals
from scrapy.http.headers import Headers
from fake_useragent import FakeUserAgent

# useful for handling different item types with a single interface
# from itemadapter import is_item, ItemAdapter

fake_user_agent: FakeUserAgent = FakeUserAgent(browsers=["chrome", "edge", "firefox", "safari", "opera"])
fake_accept_header = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
fake_accept_language = "ru-RU,ru;q=0.5"
fake_accept_encoding = "gzip, deflate, bz"
fake_upgrade_insecure_requests = "1"
fake_cache_control = "no-cache"
fake_connection = "keep-alive"
fake_sec_fetch_dest = "document"
fake_sec_fetch_mode = "navigate"
fake_sec_fetch_site = "same-origin"


def _get_headers(http_header_referer: str):
    return Headers({
        "Accept": fake_accept_header,
        "Accept-Encoding": fake_accept_encoding,
        "Accept-Language": fake_accept_language,
        "Cache-Control": fake_cache_control,
        "Connection": fake_connection,
        # "Cookie": ...,
        "Referer": http_header_referer,
        "Sec-Fetch-Dest": fake_sec_fetch_dest,
        "Sec-Fetch-Mode": fake_sec_fetch_mode,
        "Sec-Fetch-Site": fake_sec_fetch_site,
        "Upgrade-Insecure-Requests": fake_upgrade_insecure_requests,
        "User-Agent": fake_user_agent.random,
    })


class BaseFakeHttpHeadersMiddleware:
    @classmethod
    def from_crawler(cls, crawler, http_header_referer: str = 'https://www.google.com/search?q=otzovik'):
        return cls(crawler.settings, http_header_referer)

    def __init__(self, settings, http_header_referer: str = 'https://www.google.com/search?q=otzovik'):
        self.headers_list = []
        self._get_headers_list(http_header_referer)

    def _get_headers_list(self, http_header_referer: str = 'https://www.google.com/search?q=otzovik', size: int = 10):
        self.headers_list = [_get_headers(http_header_referer) for _ in range(size)]

    def process_request(self, request, spider):
        random_index = randint(0, len(self.headers_list) - 1)
        random_browser_header = self.headers_list[random_index]
        request.headers = random_browser_header


class ScraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ScraperDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
