import subprocess
from json import loads
import logging as log

from celery import Task
from typing import Type

from scrapy import Spider, Item

from config import settings


class BaseScraperTask(Task):
    logger = log.getLogger('scraper_worker_logger')

    def run(self, *args, **kwargs) -> list[dict]:
        pass

    @staticmethod
    def start_sub_process_spider(spider_cls: Type[Spider], **kwargs):
        cmd = ["scrapy", "crawl", spider_cls.name]
        for key, value in kwargs.items():
            if isinstance(value, list):
                cmd.append("-a")
                cmd.append(f"{key}={' '.join(str(x) for x in value)}")
            else:
                cmd.append("-a")
                cmd.append(f"{key}='{value}'")
        cmd.append("-o")
        cmd.append(settings.SCRAPER_BUFFER_FILE_PATH)

        subprocess.run(cmd)

    @staticmethod
    def extract_from_buffer() -> list[Item]:
        try:
            with open(settings.SCRAPER_BUFFER_FILE_PATH, 'r+', encoding='utf-8') as json_file:
                data = json_file.read()
                data = loads(data)
                json_file.truncate(0)
        except Exception:
            pass

        return data
