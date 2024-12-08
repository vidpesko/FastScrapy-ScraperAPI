# Selection of utils functions used by scraper
import dataclasses, json
from unicodedata import normalize


# Data formatting utils
def cleanse_str(input: str) -> str:
    """
    Remove all unnecessary characters from string, such as new line chars, whitespace,...
    """

    # Remove \n
    input = input.replace("\n", "")

    # Strip str
    input = input.strip()

    # Remove duplicate spaces
    input = " ".join(input.split())

    # Normalize it
    input = normalize("NFKD", input)

    # If string is "/", set it to ""
    input = "" if input == "/" else input

    return input


def str_to_int(input: str, replace_unit: str = "€") -> int | None:
    """
    Convert verbose number as string (19.00 $) to int
    """

    # Remove .
    input = input.replace(".", "")

    # Remove whitespace
    input = input.replace(" ", "")

    # Remove unit
    input = input.replace(replace_unit, "")

    # Strip it
    input = input.strip()

    # Convert it to int or float
    try:
        if input.find(",") != -1:
            # If number is float
            input = float(input)
        else:
            input = int(input)
    except ValueError:
        return None

    return input


set_empty_val_to_none = lambda x: x if x else None
