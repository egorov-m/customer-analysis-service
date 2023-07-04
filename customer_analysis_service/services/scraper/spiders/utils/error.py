import logging as log
from functools import wraps

from scrapy.exceptions import NotSupported
from scrapy.http import Response

logger = log.getLogger('http_error_logger')


def handle_http_errors(func):
    @wraps(func)
    def wrapper(self, response: Response, **kwargs):
        if response.status == 200:
            return func(self, response)
        else:
            logger.info('ERROR_RESPONSE_CODE')
            center: str = response.xpath('//center/text()').get()
            if center is not None and center.__contains__('временно запрещен,'):
                msg: str = 'Access to the site is denied, IP address is not valid!'
                logger.info(msg)
                raise NotSupported(msg)
            else:
                # !!! Captcha processing !!!
                pass

    return wrapper
