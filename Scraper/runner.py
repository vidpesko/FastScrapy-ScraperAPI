import typing
import time

import scrapy

from settings import DOWNLOADER_MIDDLEWARES, ITEM_PIPELINES
from spiders.spider import VehicleSpider
from middlewares import ScraperAPIMiddleware


def run_spider(Spider: typing.Type[scrapy.Spider]):
    spider = Spider()

    for request in spider.start_requests():
        middleware = ScraperAPIMiddleware()
        response = middleware.process_request(request, spider)

        for item in spider.parse(response):
            print(item)


if __name__ == "__main__":
    start = time.perf_counter()
    run_spider(VehicleSpider)
    print("Execution took:", time.perf_counter() - start, "seconds")
