from ast import literal_eval

import scrapy, time

from ..items import Vehicle, VehicleLoader, Error
from .translation_tables import CAR_BASIC_PROPERTY_DATA, CAR_METADATA_PARSING_TABLE, CAR_METADATA_VALUES_TABLE
from ..utils.parsing_utils import get_table_title


class VehicleSpider(scrapy.Spider):
    name = "vehicle"

    allowed_domains = ["avto.net"]
    start_urls = [
        # "https://www.avto.net/Ads/details.asp?id=20315148&display=Volkswagen%20Tiguan",
        # "https://www.avto.net/Ads/details.asp?id=20231532&display=Volkswagen%20Jetta",
        "https://www.avto.net/Ads/details.asp?ID=20178302",
    ]

    def __init__(self, start_urls = None, name = None, **kwargs):
        super().__init__(name, **kwargs)
        # Check if start_urls have been provided as argument to init

        if start_urls:
            self.start_urls = start_urls

        if kwargs.get("urls"):
            self.start_urls = literal_eval(kwargs["urls"])

        if kwargs.get("url"):
            self.start_urls = [kwargs["url"], ]

    def start_requests(self):
        # GET request
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={"use_scraperapi": True},
            )

    def parse(self, response, **kwargs):
        # Initialise and set all attributes on Item object
        vehicle = VehicleLoader(item=Vehicle(), response=response)

        # Add URL & check availability
        is_error = "".join(response.css("h4 *::text").getall()).find("Napaka")
        if is_error != -1:
            # If error has occured (due to faulty link, expired offer,...)
            # Get error message
            error_msg = " ".join(response.css(".GO-Shadow-B *::text").getall())

            yield Error(url=response.url, error_code=404, description="Listing not found. Has it expired?", error_message=error_msg)
            return  # Exit to avoid running the rest of the code

        vehicle.add_value("url", response.url)

        # Name
        raw_name_selector = response.css("h3")[0]
        vehicle.add_value("name", raw_name_selector.css("::text").get())
        vehicle.add_value("full_name", "".join(raw_name_selector.css("*::text").getall()))

        # Price
        vehicle.add_css("price", ".h2 *::text")  # Regular price, without any modifiers (discounts,...)
        vehicle.add_xpath(
            "discount_price",
            "normalize-space(//p[contains(@class, 'GO-OglasDataStaraCena')]/following-sibling::p[1][contains(@class, 'h2')]/span/text())",
        )  # Discounted price

        # Basic property table
        basic_table_selector = response.xpath(
            "//div[contains(., 'Prevoženih')]/ancestor::div[contains(@class, 'col-12')][1]"
        )[1]
        raw_properties = {property.css(".text-muted::text").get(): property.css("h5::text").get() for property in basic_table_selector.css(".col-6")}
        # Enumerate translation table and use specified properties
        properties = {CAR_BASIC_PROPERTY_DATA.get(key, key):value for key, value in raw_properties.items()}
        for key, value in properties.items():
            try:
                vehicle.add_value(key, value)
            except KeyError:
                pass

        # Comment below basic property table
        try:
            comment_selector = basic_table_selector.css(".row")[1]
            vehicle.add_value("comment", comment_selector.css("*::text").getall())
        except IndexError:
            pass

        # Description
        vehicle.add_xpath("description", "//div[@id='StareOpombe']/node()")

        # Tables
        metadata = {}
        tables_selector = response.xpath(
            "//div[contains(@class, 'col-12') and .//table[thead/tr/th[contains(text(), 'Osnovni podatki')]]]/table"
        )  # Select all tables
        # Enumerate all tables and add values to metadata dict
        for table in tables_selector:
            # Get table title
            table_title = get_table_title(table)
            # Check if table is defined in CAR_METADATA_PARSING_TABLE
            if table_title not in CAR_METADATA_PARSING_TABLE:
                continue
            table_handle_dict = CAR_METADATA_PARSING_TABLE[table_title]
            # Get and execute parsing function from CAR_METADATA_PARSING_TABLE
            parsing_func = table_handle_dict["parsing_function"]
            table_data = parsing_func(table, CAR_METADATA_VALUES_TABLE)

            new_table_title = table_handle_dict["new_table_title"]
            metadata[new_table_title] = table_data

        vehicle.add_value("metadata", metadata)

        # Seller type
        vehicle.add_css("seller_type", "#DealerAddress::text")

        # Images
        vehicle.add_value("images", [img.xpath("@data-src").get() for img in response.xpath("//div[@id='lightgallery']/p")])
        vehicle.add_value("thumbnails", [
            img.xpath("@src").get()
            for img in response.xpath("//div[@class='GO-OglasThumb']/img")
        ])

        vehicle_item = vehicle.load_item()
        yield vehicle_item
