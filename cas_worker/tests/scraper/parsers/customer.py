from datetime import datetime

from scrapy.http import Response
from scrapy.selector import Selector

from cas_worker.tests.scraper.items import CustomerItem
from cas_worker.tests.scraper.spiders.utils.error import handle_http_errors


class CustomerParser:
    @classmethod
    @handle_http_errors
    def parse_customer(cls, response: Response, **kwargs):
        return CustomerParser.extract_customer_profile_data(Selector(response))

    @classmethod
    def _table_to_dict(cls,table):
        return {item.css('td')[0].css('::text').get(): item.css('td')[1].css('::text').get() for item in table}

    @classmethod
    def extract_customer_profile_data(cls, selector: Selector) -> CustomerItem:
        name_id = selector.css('div.content-left h1.login ::text').get().replace(' ', '+')
        reputation = int(
            selector.css('div.content div.content-left div.glory-box div.karma div[class^="karma"] ::text').get())
        table_selectors = 'div.content div.content-right div.columns'

        table_1 = selector.css(f'{table_selectors} table.table_1 tr')
        table_2 = selector.css(f'{table_selectors} table.table_2 tr')
        table_1_dict = cls._table_to_dict(table_1)
        table_2_dict = cls._table_to_dict(table_2)

        country_str = table_1_dict.get('Страна:')
        country = country_str if country_str is not None and country_str != '<Нет>' else None
        city_str = table_1_dict.get('Город:')
        city = city_str if city_str is not None and city_str != '<Нет>' else None
        profession = table_1_dict.get('Профессия:')

        reg_date_str: str = table_1_dict.get('Регистрация:')
        month_dict = {'янв': '01', 'фев': '02', 'мар': '03', 'апр': '04', 'май': '05', 'мая': '05', 'июн': '06',
                      'июл': '07', 'авг': '08', 'сен': '09', 'окт': '10', 'ноя': '11', 'дек': '12'}
        for key, value in month_dict.items():
            reg_date_str = reg_date_str.replace(key, value)
        if len(reg_date_str.split(' ')) == 2:  # the date can be specified without the year, if the year is current
            reg_date_str += f' {datetime.now().year}'
        reg_date = datetime.strptime(reg_date_str, '%d %m %Y').date()
        count_subscribers = int(table_2_dict.get('Подписчиков:'))

        customer = CustomerItem()
        customer['name_id'] = name_id
        customer['reputation'] = reputation
        customer['country_ru'] = country
        customer['city_ru'] = city
        customer['profession'] = profession
        customer['reg_date'] = reg_date
        customer['count_subscribers'] = count_subscribers
        # customer['last_activity_date'] = last_activity_date

        return customer
