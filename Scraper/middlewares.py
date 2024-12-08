# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import asyncio, time

from scrapy import signals
from scrapy.http import HtmlResponse

import nodriver as uc

from scraperapi.client import ScraperApiClient


class ScraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ScraperDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class NoDriverMiddleware:
    """
    Custom Scrapy download middleware to route requests via nodriver package
    """
    def __init__(self):
        self.browser = None

    @classmethod
    def from_crawler(cls, crawler):
        # Initialize the middleware and start the browser
        instance = cls()
        # instance.browser = uc.loop().run_until_complete(instance.open_browser())
        # crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
        # crawler.signals.connect(instance.spider_closed, signal=signals.spider_closed)
        return instance

    async def process_request(self, request, spider):
        # Use NoDriver to fetch the page
        if request.meta.get("use_nodriver", False):  # Use NoDriver only for specific requests
            spider.logger.info(f"Processing request with NoDriver: {request.url}")
            start_time = time.perf_counter()
            # Open browser
            if not self.browser:
                browser_st = time.perf_counter()
                self.browser = await uc.start()
                print("Browser opened in", time.perf_counter() - browser_st)

            # Get HTML
            page_st = time.perf_counter()
            page = await self.browser.get(request.url)
            print("Page opened in", time.perf_counter() - page_st)

            await asyncio.sleep(0.5)
            html_st = time.perf_counter()
            content = await page.get_content()
            print("HTML collected in", time.perf_counter() - html_st)
            # Close everything
            await page.close()
            self.browser.stop()

            spider.logger.info(f"Page was closed. Request finished in: {time.perf_counter() - start_time}seconds")

            # Create an HtmlResponse with the fetched content
            print("Custom middleware finished in", time.perf_counter() - start_time)
            return HtmlResponse(
                url=request.url,
                body=content,
                encoding="utf-8",
                request=request,
            )

        return None  # Allow other requests to proceed as normal

    async def open_browser(self):
        return await uc.start()

    def spider_opened(self, spider):
        # spider.test = self.something
        print("1.) OPENED", self.browser)

    def spider_closed(self, spider):
        print("3.) CLOSED")


class ScraperAPIMiddleware:
    """
    Custom Scrapy download middleware to route requests via custom ScraperAPI package
    """
    def __init__(self):
        self.browser = None

    def process_request(self, request, spider):
        # Use NoDriver to fetch the page
        if request.meta.get("use_scraperapi", False):  # Use NoDriver only for specific requests
            spider.logger.info(f"Processing request with NoDriver: {request.url}")
            start_time = time.perf_counter()

            client = ScraperApiClient("amqp:://localhost/", "avtonet_api_queue")
            client.connect()
            content = client.get(request.url)

            spider.logger.info(f"Page was closed. Request finished in: {time.perf_counter() - start_time}seconds")

            # Create an HtmlResponse with the fetched content
            # print("Custom middleware finished in", time.perf_counter() - start_time)
            return HtmlResponse(
                url=request.url,
                body=content["html"],
                encoding="utf-8",
                request=request,
            )

        return None  # Allow other requests to proceed as normal


class TimingMiddleware:
    def __init__(self):
        self.start_time = None

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def spider_opened(self):
        self.start_time = time.perf_counter()

    def spider_closed(self):
        elapsed_time = time.perf_counter() - self.start_time
        print(f"Spider run time: {elapsed_time:.2f} seconds")
