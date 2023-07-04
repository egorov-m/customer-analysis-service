from scrapy import Item, Spider


class TruncateTextPipeline(object):
    @staticmethod
    def process_item(item: Item, spider: Spider):
        if 'text_comment' in item:
            item['text_comment'] = TruncateTextPipeline.trim_text(item['text_comment'], 10000)
        elif 'description' in item:
            item['description'] = TruncateTextPipeline.trim_text(item['description'], 5000)
        elif 'text_review' in item:
            item['text_review'] = TruncateTextPipeline.trim_text(item['text_review'], 30000)

        return item

    @staticmethod
    def trim_text(text: str, max_length: int = 3000):
        if len(text) > max_length:
            return text[:max_length].strip()
        return text
