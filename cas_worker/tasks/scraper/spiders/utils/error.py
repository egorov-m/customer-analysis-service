import logging as log
from functools import wraps

import requests
from scrapy import Request
from scrapy.exceptions import NotSupported
from scrapy.http import Response

logger = log.getLogger('http_error_logger')


def handle_http_errors(func):
    @wraps(func)
    def wrapper(self, response: Response, **kwargs):
        request: Request = response.request

        if response.status == 200:
            return func(self, response)
        else:
            logger.info('ERROR_RESPONSE_CODE')
            center: str = response.xpath('//center/text()').get()
            if center is not None and center.__contains__('временно запрещен,'):
                msg: str = 'Access to the site is denied, IP address is not valid!'
                logger.info(msg)
                raise NotSupported(msg)
            elif center is not None and center.__contains__('Технический перерыв 1 час'):
                logger.info('ERROR_FAKE_TECHNICAL_BREAK')
                request.headers.__delitem__('Cookie')
                return request.replace(meta={'dont_merge_cookies': True}, dont_filter=True)
            else:
                logger.info('ERROR_CAPTCHA')
                img_src = response.css("img ::attr(src)").get()
                img_captcha = requests.get(f'https://otzovik.com{img_src}',
                                           stream=True,
                                           headers=request.headers.to_unicode_dict()).content
                # Captcha processing !!!

    return wrapper
