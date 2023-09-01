import subprocess
import sys
from json import loads
import logging as log

from celery import Task
from typing import Type

from scrapy import Spider, Item


class BaseScraperTask(Task):
    logger = log.getLogger('scraper_worker_logger')

    def run(self, *args, **kwargs) -> list[dict]:
        pass

    @staticmethod
    def start_sub_process_spider(spider_cls: Type[Spider], **kwargs):
        cmd = [sys.executable.replace("python", "scrapy"), "crawl", spider_cls.name]
        for key, value in kwargs.items():
            if isinstance(value, list):
                cmd.append("-a")
                cmd.append(f"{key}={' '.join(str(x) for x in value)}")
            else:
                cmd.append("-a")
                cmd.append(f"{key}={value}")
        cmd.append("-o")
        cmd.append("-:json")  # stdout

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, encoding="utf-8")
        out = process.communicate()[0].replace("[0m", "")
        return out

    @staticmethod
    def get_list_item(data_json: str) -> list[Item]:
        return loads(data_json) if data_json is not None else []
