import json
from itertools import product

import requests

from utility.constants import (
    ENUM,
    TYPE,
    DESCRIPTION,
    DEFAULT,
    MINIMUM,
    MAXIMUM,
    PROPERTIES,
    SCATTER,
    BAR,
    HEATMAP,
    CONTOUR,
    BOX,
    VIOLIN,
    HISTOGRAM,
    HISTOGRAM2D,
    SCATTER3D,
    MESH3D,
    LAYOUT,
    OBJECT,
    ARRAY_STRING,
    ITEMS,
    ATTRIBUTES,
    LAYOUT_ATTRIBUTES,
    TITLE,
    SCATTERGEO,
    SCATTERMAPBOX,
    ANYOF,
    STRING,
)

PLOTLY_TYPE = "valType"
PLOTLY_VALUES = "values"
ENUMERATED = "enumerated"
MIN = "min"
MAX = "max"
PLOTLY_DEFAULT = "dflt"
FLAGS = "flags"
EXTRAS = "extras"
ROLE = "role"

SCHEMA = "schema"
TRACES = "traces"
SYMBOL = "symbol"

# Build new plotly schemas with only specified graph configurations
PLOT_TYPE_LIST = [
    SCATTER,
    BAR,
    HEATMAP,
    CONTOUR,
    BOX,
    VIOLIN,
    HISTOGRAM,
    HISTOGRAM2D,
    SCATTER3D,
    MESH3D,
    SCATTERGEO,
    SCATTERMAPBOX,
]


def all_combos(flaglist: list) -> list:
    """
    return all permutations of the elements in flaglist delimited by +
    matches what plotly takes as input
    :param flaglist:
    :return:
    """
    N = len(flaglist)
    combos = []
    bool_values = [False, True]
    for bool_list in product(bool_values, repeat=N):
        if any(bool_list):
            combos.append(
                "+".join([val for val, in_list in zip(flaglist, bool_list) if in_list])
            )
    return combos


def build_dict_from_role_object(plotly_dict: dict, is_dict: bool = True) -> dict:
    """
    a recursive function that takes in a plotly api dict and transforms it to json schema format
    """
    # blacklist if for keys that we are not going to put into our wizard
    blacklist = [
        "stream",
        "transforms",
        "tickformatstops",
        "_deprecated",
        "impliedEdits",
        "r",
        "t",
        "hovertext",
        "uid",
        "ids",
        "customdata",
    ]
    new_dict = {TYPE: OBJECT if is_dict else ARRAY_STRING}
    property_dict = {}
    inner_attributes = plotly_dict if is_dict else plotly_dict[ITEMS]
    for key, plotly_value in inner_attributes.items():
        if (
            key not in blacklist
            and (not key.endswith("src"))  # gets rid of keys for "Plotly Chart Studio"
            and isinstance(plotly_value, dict)
        ):
            if ROLE in plotly_value:
                if plotly_value[ROLE] == OBJECT:
                    # plotly_value is a dictionary of dictionaries
                    # if ITEMS in plotly_value the the dictionary represents should be changed to type array in
                    # json schema
                    property_dict[key] = build_dict_from_role_object(
                        plotly_value, is_dict=(ITEMS not in plotly_value)
                    )
                else:
                    # Keys that point to anything that is not an object or array
                    # We are handling the key symbol separately
                    if key == SYMBOL:
                        property_dict[key] = symbol_dict(plotly_value)
                    else:
                        property_dict[key] = build_dict_from_plotly_one_level_dict(
                            plotly_value
                        )
    if property_dict:
        new_dict[PROPERTIES if is_dict else ITEMS] = (
            property_dict if is_dict else property_dict[key]
        )
        if not is_dict:
            new_dict[TITLE] = key
    return new_dict


def build_dict_from_plotly_one_level_dict(plotly_dict: dict) -> dict:
    """
    Converts non nested plotly api dict and transforms it to json schema format
    """
    type_dict = {
        "enumerated": "string",
        "boolean": "boolean",
        "number": "number",
        "integer": "integer",
        "string": "string",
        "angle": "number",
    }
    val_type = plotly_dict[PLOTLY_TYPE]
    new_dict = {TYPE: type_dict.get(val_type, "string")}
    for item, corresp_item in zip(
        [DESCRIPTION, PLOTLY_DEFAULT], [DESCRIPTION, DEFAULT]
    ):
        if item in plotly_dict:
            new_dict[corresp_item] = plotly_dict[item]
    if val_type == "flaglist":
        new_dict[ENUM] = all_combos(plotly_dict[FLAGS]) + plotly_dict.get(EXTRAS, [])
    if val_type == "enumerated":
        new_dict[ENUM] = plotly_dict[PLOTLY_VALUES]
    if val_type == "integer" or val_type == "number":
        for item, corresp_item in zip([MIN, MAX], [MINIMUM, MAXIMUM]):
            if item in plotly_dict:
                new_dict[corresp_item] = plotly_dict[item]
    if val_type == "angle":
        new_dict[MINIMUM] = -180
        new_dict[MAXIMUM] = 180
    return new_dict


def symbol_dict(plotly_dict: dict) -> dict:
    """
    We do not make the 474 options for symbols seen in our wizard e.g. star-triangle-down-open-dot
    :param plotly_dict:
    :return:
    """
    reduced_symbols = [
        "circle",
        "square",
        "diamond",
        "cross",
        "x",
        "triangle-up",
        "triangle-down",
        "pentagon",
        "hexagon",
        "octagon",
        "star",
    ]

    new_dict = {TYPE: "string"}
    for item, corresp_item in zip(
        [DESCRIPTION, PLOTLY_DEFAULT], [DESCRIPTION, DEFAULT]
    ):
        if item in plotly_dict:
            new_dict[corresp_item] = plotly_dict[item]
    new_dict[ENUM] = reduced_symbols
    return new_dict


def parse_plotly_api_into_schemas():
    # get api request from plotly and convert to type dictionary
    response = requests.get("https://api.plot.ly/v2/plot-schema?sha1=%27%27").text
    plotly_full = json.loads(response)
    assert isinstance(plotly_full, dict)
    for plot_type in PLOT_TYPE_LIST:
        plotly_type_dict = plotly_full[SCHEMA][TRACES][plot_type]
        json_schema = {
            ATTRIBUTES: build_dict_from_role_object(plotly_type_dict[ATTRIBUTES])[
                PROPERTIES
            ]
        }
        if LAYOUT_ATTRIBUTES in plotly_type_dict:
            json_schema[LAYOUT_ATTRIBUTES] = build_dict_from_role_object(
                plotly_type_dict[LAYOUT_ATTRIBUTES]
            )[PROPERTIES]
            # todo: move plotly_api to graphics folder
        with open(f"plotly_api/{plot_type}_plotly_schema.json", "w") as outfile:
            json.dump(json_schema, outfile, indent=4)
    json_schema = build_dict_from_role_object(
        plotly_full[SCHEMA][LAYOUT][LAYOUT_ATTRIBUTES]
    )
    # this needs to be changed to handle string and array input
    source_dict = json_schema[PROPERTIES]["mapbox"][PROPERTIES]["layers"][ITEMS][
        PROPERTIES
    ]["source"]
    source_dict = {
        DESCRIPTION: source_dict[DESCRIPTION],
        ANYOF: [{TYPE: STRING}, {TYPE: ARRAY_STRING, ITEMS: {TYPE: STRING}}],
    }
    json_schema[PROPERTIES]["mapbox"][PROPERTIES]["layers"][ITEMS][PROPERTIES][
        "source"
    ] = source_dict
    with open("plotly_api/layout_plotly_schema.json", "w") as outfile:
        json.dump(json_schema, outfile, indent=4)


# todo: move this script to scripts or utilities folder
if __name__ == "__main__":
    parse_plotly_api_into_schemas()
