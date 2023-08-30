# Scrapy settings for scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "scraper"

SPIDER_MODULES = ["cas_worker.tasks.scraper.spiders"]
NEWSPIDER_MODULE = "cas_worker.tasks.scraper.spiders"

LOG_FILE = "./.scrapy/log"
LOG_STDOUT = False

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
   "Accept-Language": "en-US,en;q=0.5",
   "Upgrade-Insecure-Requests": "1",
   "Sec-Fetch-Dest": "document",
   "Sec-Fetch-Mode": "navigate",
   "Sec-Fetch-Site": "same-origin",
   "Sec-Fetch-User": "?1",
   "Sec-GPC": "1",
   "Pragma": "no-cache",
   "Cache-Control": "no-cache",
   "Referrer": "https://www.google.com/search?q=otzovik",
   # "DNT": 1,
   'Connection': 'keep-alive',
}

# variable is not used, it's just an example
# This set of cookies is needed to bypass captcha locks and emulate a real user
DEFAULT_REQUEST_COOKIES = {
   'ROBINBOBIN': '...',
   'ssid': '...',
   'refreg': '...',  # optional
   'csid': '...'  # optional
}

# LOG_LEVEL = 'INFO'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 5

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_DELAY = 7
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 5
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    "scrapy.spidermiddlewares.httperror.HttpErrorMiddleware": 100,
    "scrapy.spidermiddlewares.referer.RefererMiddleware": True
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware": None,
    "cas_worker.tasks.scraper.middleware.fake_http_headers.BaseFakeHttpHeadersMiddleware": 400,

    # "rotating_proxies.middlewares.RotatingProxyMiddleware": 610,
    # "rotating_proxies.middlewares.BanDetectionMiddleware": 620,
    "scrapy.downloadermiddlewares.cookies.CookiesMiddleware": 700,  # 700
}

ROTATING_PROXY_LIST_PATH = "./.scrapy/httpproxy/list.txt"
# ROTATING_PROXY_PAGE_RETRY_TIMES =
# ROTATING_PROXY_CLOSE_SPIDER = True

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "cas_worker.tasks.scraper.pipelines.clean.CleanTextPipeline": 301,
    "cas_worker.tasks.scraper.pipelines.truncate.TruncateTextPipeline": 302,
    "cas_worker.tasks.scraper.pipelines.translate.TranslateCustomerGeoLocationPipeline": 303,
    "cas_worker.tasks.scraper.pipelines.db.DbPostgresPipeline": 304,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [100, 101, 102, 103, 201, 202, 203, 204, 205, 206,
                               207, 208, 226, 300, 301, 302, 303, 304, 305, 306,
                               307, 308, 400, 401, 402, 403, 404, 405, 406, 407,
                               408, 409, 410, 411, 412, 413, 414, 415, 416, 417,
                               418, 421, 422, 423, 424, 426, 428, 429, 431, 451,
                               499, 500, 501, 502, 503, 504, 505, 506, 507, 508,
                               510, 511]
# [301, 302, 429, 499, 507]
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.DbmCacheStorage"  # "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
