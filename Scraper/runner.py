import sys
import typing
import time
import importlib
import pkgutil
from types import ModuleType

import scrapy
from scrapy.utils.spider import iter_spider_classes

from .settings import ITEM_PIPELINES
from .middlewares import ScraperAPIMiddleware
from . import pipelines


def load_pipelines(pipelines_dict: list[dict]) -> list[ModuleType]:
    ordered_pipelines = list(pipelines_dict.items())
    ordered_pipelines.sort(key=lambda x: x[1])

    # Import pipelines
    imported_pipelines = []
    for pipeline in ordered_pipelines:
        # Split the module and class name
        module_name, class_name = pipeline[0].rsplit(".", 1)
        cls = getattr(pipelines, class_name)
        cls_instance = cls()
        imported_pipelines.append(cls_instance)

    return imported_pipelines


def get_spider_from_name(spider_name, spiders_module= "Scraper.spiders") -> typing.Type[scrapy.Spider]:
    print(sys.path)
    module = importlib.import_module(spiders_module)

    for _, module_name, is_pkg in pkgutil.iter_modules(module.__path__):
        if not is_pkg:
            spider_module = importlib.import_module(f"{spiders_module}.{module_name}")
            for cls in iter_spider_classes(spider_module):
                if cls.name == spider_name:
                    return cls()

    raise ValueError(f"No spider with name '{spider_name}' exists")


def run_spider(Spider: typing.Type[scrapy.Spider] | str) -> list[scrapy.Item]:
    imported_pipelines = load_pipelines(ITEM_PIPELINES)

    # If spider name is provided
    if isinstance(Spider, str):
        spider = get_spider_from_name(Spider)
    else:
        spider = Spider()

    output = []

    for request in spider.start_requests():
        # For every request, use custom middleware to fetch requests via ScraperAPI
        middleware = ScraperAPIMiddleware()
        response = middleware.process_request(request, spider)

        # Process items using pipelines
        for item in spider.parse(response):
            for pipeline in imported_pipelines:
                item = pipeline.process_item(item, spider)
            output.append(item)

    return output


if __name__ == "__main__":
    start = time.perf_counter()
    items = run_spider("vehicle")
    print(items)
    print("Execution took:", time.perf_counter() - start, "seconds")
