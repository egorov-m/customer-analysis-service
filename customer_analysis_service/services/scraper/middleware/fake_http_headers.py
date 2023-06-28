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

    def _get_headers_list(self, http_header_referer: str, size: int = 10):
        self.headers_list = [_get_headers(http_header_referer) for _ in range(size)]

    def process_request(self, request, spider):
        random_index = randint(0, len(self.headers_list) - 1)
        random_browser_header = self.headers_list[random_index]
        request.headers = random_browser_header
