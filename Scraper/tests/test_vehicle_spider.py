"""
Tests for VehicleSpider defined in spiders/vehicle_spider.py
"""

import pytest
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.signalmanager import dispatcher

from ..items import Vehicle


TEST_VEHICLE_URLS = [
    "https://www.avto.net/Ads/details.asp?id=20305237&display=Audi%20A7",  # Most basic url, simple price, sold by person not company
    "https://www.avto.net/Ads/details.asp?id=20311825&display=Ssangyong%20Rexton",  # Price is crossed, discounted price is given
]


@pytest.fixture(scope="module")
def response() -> list[Vehicle]:
    """
    Fixture to run VehicleSpider and return all yielded items
    """

    results = []

    def crawler_results(signal, sender, item, response, spider):
        results.append(item)

    process = CrawlerProcess(get_project_settings())

    dispatcher.connect(crawler_results, signal=signals.item_scraped)

    process.crawl("vehicle", TEST_VEHICLE_URLS)
    process.start()  # the script will block here until the crawling is finished

    return results


@pytest.fixture
def response_single(response) -> Vehicle:
    """
    Return only the first item in response
    """

    return response[0]


def test_thumbnails_not_null(response):
    for vehicle in response:
        assert all(vehicle.thumbnails)


def test_price(response):
    for vehicle in response:
        # Test case 1: price should never be zero
        assert vehicle.price != 0
        # Test case 2: discount_price should always be lower than price
        if vehicle.discount_price:
            assert vehicle.price > vehicle.discount_price
        # Test case 3: if price is none, price_verbose should have value
        # if not vehicle.price:
        #     assert vehicle.price_verbose is not None


def test_registration(response):
    for vehicle in response:
        # Test case 1: if new_vehicle is True, first_registration should be None
        if vehicle.new_vehicle:
            assert not vehicle.first_registration