"""
Collection of translation tables. Translation table is used to convert human readable property names on website
and turn them into machine-friendly
"""
from ..utils.parsing_utils import parse_table, parse_other_data_table


# On car page this is the first table, right below images
CAR_BASIC_PROPERTY_DATA = {
    "Prva registracija": "first_registration",
    "Starost": "new_vehicle",
    "Prevoženih": "mileage",
    "Lastnikov": "num_of_owners",
    "Vrsta goriva": "fuel_type",
    "Moč motorja": "engine_power",
}

# Car page tables
CAR_METADATA_VALUES_TABLE = {
    "Motor": "engine"
}

# Translation table, that tells how to parse table
CAR_METADATA_PARSING_TABLE = {
    "Osnovni podatki": {
        "new_table_title": "basic_data",
        "parsing_function": parse_table,
    },
    "Poraba goriva in emisije (WLTP)": {
        "new_table_title": "emission_data",
        "parsing_function": parse_table,
    },
    "Poraba goriva in emisije (NEDC)": {
        "new_table_title": "emission_data",
        "parsing_function": parse_table,
    },
    "Oprema in ostali podatki o ponudbi": {
        "new_table_title": "other_data",
        "parsing_function": parse_other_data_table,
    },
}
