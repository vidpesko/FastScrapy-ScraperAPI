"""
Collection of HTML parsing function
"""
from urllib.parse import parse_qs, urlparse

import scrapy.selector

from .formatting_utils import cleanse_str


def get_table_title(table_selector: scrapy.selector):
    """Get header / title of HTML table

    Args:
        table_selector (scrapy.selector): table selector
    """

    return cleanse_str(table_selector.css("thead tr th::text").get())


def parse_table(
    table_selector: scrapy.selector,
    translation_table: dict,
) -> dict:
    """Parse HTML table and return its data as dict

    Args:
        table_selector (scrapy.selector): table selector
        translation_table (dict): translation table for table th values

    Returns:
        dict: returns dict of table data.
    """

    table_data = {}

    for row in table_selector.css("tbody tr"):
        header = row.css("th::text").get()
        value = row.css("td::text").get()

        if not header:
            continue

        # Format
        header = cleanse_str(header).replace(":", "")
        new_header = translation_table.get(header, header)
        value = cleanse_str(value)

        if not value:
            continue

        table_data[new_header] = value

    return table_data


def parse_other_data_table(
        table_selector: scrapy.selector,
        translation_table: dict
    ) -> dict:
    """Parse HTML table and return its data as dict

    Args:
        table_selector (scrapy.selector): table selector
        translation_table (dict): translation table for table th values

    Returns:
        dict: returns dict of table data.
    """

    table_data = {}
    rows = table_selector.css("tbody tr")
    for header_row, value_row in zip(rows[::2], rows[1::2]):
        # Extract header
        header = list(map(cleanse_str, header_row.css("*::text").getall()))
        header = next(h for h in header if h).replace(":", "")
        # Extract values
        values = []
        for val in value_row.css("ul li::text"):
            value = cleanse_str(val.get())
            values.append(value)
        # Add to output
        table_data[header] = values

    return table_data


def get_id_from_url(url: str) -> int:
    """Get id from avto.net url

    Args:
        url (str): avto.net vehicle url

    Returns:
        int: id
    """

    parsed_url = urlparse(url)
    try:
        id = (
            parse_qs(parsed_url.query)["id"][0]
            if parse_qs(parsed_url.query).get("id", False)
            else parse_qs(parsed_url.query)["ID"][0]
        )
        return int(id)
    except (IndexError, KeyError):
        raise Exception(f"Url '{url}' does not have id parameter")
    except ValueError:
        raise ValueError(f"Vehicle id extracted from url '{url}' can not be parsed to integer")
