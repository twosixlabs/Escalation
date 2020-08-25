# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import copy

from graphics.plotly_plot import LAYOUT
from utility.constants import *

X = "x"
Y = "y"
Z = "z"
MODE = "mode"

BAR = "bar"
HEATMAP = "heatmap"
HEATMAPGL = "heatmapgl"
CONTOUR = "contour"
BOX = "box"
VIOLIN = "violin"
HISTOGRAM = "histogram"
HISTOGRAM2D = "histogram2d"
HISTOGRAM2DCONTOUR = "histogram2dcontour"
SCATTER3D = "scatter3d"
# SURFACE = "surface"
MESH3D = "mesh3d"


SELECTOR_DICT = {
    SCATTER: "Scatter or Line Plot",
    BAR: "Bar Plot",
    HEATMAP: "Heatmap",
    CONTOUR: "Contour Plot",
    BOX: "Box Plot",
    VIOLIN: "Violin Plot",
    HISTOGRAM: "Histogram",
    HISTOGRAM2D: "2D Histogram",
    SCATTER3D: "3D Scatter/Line Plot",
    MESH3D: "3D Mesh Plot",
}


def build_plotly_schema(column_names):
    if column_names:
        column_names.sort()
    schema = {
        "$schema": "http://json-schema.org/draft/2019-09/schema#",
        "title": "plotly graph definition",
        "description": "dictionary that follows https://plotly.com/javascript/reference/",
        "type": "object",
        "required": [DATA],
        "properties": {
            DATA: {
                "type": "array",
                "description": "list of graphs to be plotted on a single plot",
                MIN_ITEMS: 1,
                "items": {
                    "type": "object",
                    "title": "Data Dictionary",
                    "required": ["type"],
                    "properties": {
                        "type": {
                            "type": "string",
                            TITLE: "Plot Type",
                            "enum": [
                                "scatter",
                                "scattergl",
                                "bar",
                                "pie",
                                "heatmap",
                                "heatmapgl",
                                "image",
                                "contour",
                                "table",
                                "box",
                                "violin",
                                "histogram",
                                "histogram2d",
                                "histogram2dcontour",
                                "scatter3d",
                                "surface",
                                "mesh3d",
                            ],
                        },
                        X: {
                            "type": "string",
                            TITLE: "Data on X Axis",
                            "enum": column_names,
                        },
                        Y: {
                            "type": "string",
                            TITLE: "Data on Y Axis",
                            "enum": column_names,
                        },
                        Z: {
                            "type": "string",
                            TITLE: "Data on Z Axis",
                            "enum": column_names,
                        },
                        "mode": {
                            "type": "string",
                            TITLE: "Graph Style",
                            "description": "used for scatter or scattergl",
                            "enum": [
                                "markers",
                                "lines",
                                "text",
                                "lines+markers",
                                "markers+text",
                                "lines+text",
                                "lines+markers+text",
                                "none",
                                "group",
                            ],
                        },
                    },
                },
            },
            LAYOUT: {
                "title": "Graph layout",
                "description": "Determines how the graph looks",
                "type": "object",
                "properties": {
                    "height": {"type": "number", "minimum": 10},
                    "width": {"type": "number", "minimum": 10},
                    "xaxis": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "object",
                                "properties": {"text": {"type": "string"}},
                            },
                            "automargin": {"type": "boolean"},
                        },
                    },
                    "yaxis": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "object",
                                "properties": {"text": {"type": "string"}},
                            },
                            "automargin": {"type": "boolean"},
                        },
                    },
                    "hovermode": {
                        "type": "string",
                        "enum": [
                            "x",
                            "y",
                            "closest",
                            "false",
                            "x unified",
                            "y unified",
                        ],
                    },
                },
            },
        },
    }
    return schema


def build_plotly_schema_individual_dicts(column_names):
    """
    Seperate schemas for each plot
    :param column_names:
    :return:
    """
    # If the element is not in required we will delete it
    programmed_data_options = [TYPE, X, Y, Z, MODE]

    directions_for_building_schemas = {
        SCATTER: {
            ENUM: [SCATTERGL, SCATTER],
            REQUIRED: [TYPE, X, Y, MODE],
            DESCRIPTION: {
                TYPE: "scattergl uses uses WebGL which is faster for lots of points",
                MODE: "marker for scatter plot, line for line plot",
            },
        },
        BAR: {ENUM: [BAR], REQUIRED: [TYPE, X, Y],},
        BOX: {
            ENUM: [BOX],
            REQUIRED: [TYPE, Y],
            DESCRIPTION: {
                TYPE: "To show more than one box in the plot,"
                'set "group by" in visualization options below',
            },
        },
        VIOLIN: {
            ENUM: [VIOLIN],
            REQUIRED: [TYPE, Y],
            DESCRIPTION: {
                TYPE: "To show more than one violin in the plot,"
                'set "group by" in visualization options below',
            },
        },
        HISTOGRAM: {ENUM: [HISTOGRAM], REQUIRED: [TYPE, X],},
        CONTOUR: {ENUM: [CONTOUR], REQUIRED: [TYPE, X, Y, Z],},
        HISTOGRAM2D: {ENUM: [HISTOGRAM2D, HISTOGRAM2DCONTOUR], REQUIRED: [TYPE, X, Y],},
        MESH3D: {ENUM: [MESH3D], REQUIRED: [TYPE, X, Y, Z],},
        HEATMAP: {
            ENUM: [HEATMAPGL, HEATMAP],
            REQUIRED: [TYPE, X, Y, Z],
            DESCRIPTION: {
                TYPE: "heatmapgl uses WebGL which may be faster for lots of points"
            },
        },
        SCATTER3D: {
            ENUM: [SCATTER3D],
            REQUIRED: [TYPE, X, Y, Z, MODE],
            DESCRIPTION: {
                MODE: "if using line make sure your points are in a sensible order"
            },
        },
    }

    # used to figure based on type what schema should
    # be used type in config dict (used in wizard ui)
    schema_to_type = {
        schema: schema_directions[ENUM]
        for schema, schema_directions in directions_for_building_schemas.items()
    }

    dict_of_schemas = {}
    main_schema = build_plotly_schema(column_names)
    for plot_type, directions in directions_for_building_schemas.items():
        plot_schema = copy.deepcopy(main_schema)
        plot_schema[PROPERTIES][DATA][ITEMS][PROPERTIES][TYPE][ENUM] = directions[ENUM]
        plot_schema[PROPERTIES][DATA][ITEMS][REQUIRED] = directions[REQUIRED]
        # removing unnecessary elements from the general Plotly schema
        # that are not needed for this plot type
        elements_to_delete = [
            x for x in programmed_data_options if x not in directions[REQUIRED]
        ]
        for element in elements_to_delete:
            del plot_schema[PROPERTIES][DATA][ITEMS][PROPERTIES][element]
        description_dict = directions.get(DESCRIPTION, {})
        for key_in_schema, description in description_dict.items():
            plot_schema[PROPERTIES][DATA][ITEMS][PROPERTIES][key_in_schema][
                DESCRIPTION
            ] = description
        dict_of_schemas[plot_type] = plot_schema

    return dict_of_schemas, schema_to_type
