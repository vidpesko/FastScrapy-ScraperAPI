import scrapy.item

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from .items import Vehicle, Error
from .utils.formatting_utils import cleanse_str
from .utils.parsing_utils import get_id_from_url


class ErrorPipeline:
    """
    Handle errors
    """
    
    def process_item(self, item: Error, spider):
        adapter = ItemAdapter(item)

        if adapter.get("error_message"):
            adapter["error_message"] = cleanse_str(adapter["error_message"])

        return item


class VehiclePipeline:
    """
    Handle and process Vehicle item.

    Tasks:
        - add avtonet_id
        - store data to database
    """

    def process_item(self, item: Vehicle, spider):
        adapter = ItemAdapter(item)

        # Extract id
        if adapter.get("url") and not adapter.get("error_code"):
            avtonet_id = get_id_from_url(adapter.get("url"))
            if avtonet_id:
                adapter["avtonet_id"] = avtonet_id

        # Save data

        return item


class ToDictPipeline:
    """
    Convert Item to JSON serializable
    """

    def process_item(self, item: scrapy.item, spider):
        return item.to_dict()