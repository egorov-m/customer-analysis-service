from scrapy.selector import Selector

from customer_analysis_service.services.scraper.items import ProductItem


class ProductParser:
    @staticmethod
    def extract_product_info(selector: Selector):
        fullname = selector.css('a.product-name span ::text').get()
        image_url = f'https:{selector.css("div.product-photo img ::attr(src)").get()}'
        product_info = selector.css('div.product-info')

        title_block: str = str(product_info.css(".title_block ::text").get()).replace('None', '')
        text_block: str = str(product_info.css(".text_block ::text").getall()).replace('None', '').strip()
        props_block: str = ''
        for item in product_info.css('table.product-props tr'):
            key = item.css('td ::text')[0].get()
            value = item.css('td ::text')[1].get()
            props_block += f'{key}: {value}\n'

        description: str = title_block + text_block + '\n' + props_block

        product = ProductItem()
        product['name_id'] = selector.css('a.product-name ::attr(href)').get().split('/')[2]
        product['fullname'] = fullname
        product['image_url'] = image_url
        product['description'] = description

        yield product
