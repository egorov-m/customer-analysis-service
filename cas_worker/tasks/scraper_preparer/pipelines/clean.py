import re


class CleanTextPipeline(object):
    @staticmethod
    def process_item(item, spider):
        if 'description' in item:
            description = item['description']
            description = re.sub(r'\n+', '\n', description)
            description = re.sub(r'\s+', ' ', description)

            item['description'] = description

        return item
