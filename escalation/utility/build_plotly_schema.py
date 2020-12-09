# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import copy

from graphics.plotly_plot import LAYOUT, X, Y, Z, ERROR_X, ERROR_Y, ERROR_Z, ARRAY
from utility.constants import *

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

PLOT_TYPE = "plot_type"

COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

COLOR_NAMES = [
    "blue",
    "orange",
    "green",
    "red",
    "purple",
    "brown",
    "pink",
    "gray",
    "yellow-green",
    "blue-teal",
]

SELECTOR_DICT = {
    "$schema": "http://json-schema.org/draft/2019-09/schema#",
    "title": "Type of Plot",
    REQUIRED: [PLOT_TYPE],
    PROPERTIES: {
        PLOT_TYPE: {
            TYPE: "string",
            TITLE: "Plot Type",
            "enum": [
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
            ],
            OPTIONS: {
                "enum_titles": [
                    "Scatter or Line Plot",
                    "Bar Plot",
                    "Heatmap",
                    "Contour Plot",
                    "Box Plot",
                    "Violin Plot",
                    "Histogram",
                    "2D Histogram",
                    "3D Scatter/Line Plot",
                    "3D Mesh Plot",
                ]
            },
        }
    },
    OPTIONS: {DISABLE_COLLAPSE: True, DISABLE_PROPERTIES: True},
}


def build_plotly_schema(column_names):
    if column_names:
        column_names.sort()
    schema = {
        "$schema": "http://json-schema.org/draft/2019-09/schema#",
        "title": "Plotly Graph Config",
        "description": "dictionary that follows https://plotly.com/javascript/reference/",
        "type": "object",
        "required": [DATA],
        OPTIONS: {DISABLE_COLLAPSE: True, REMOVE_EMPTY_PROPERTIES: True},
        "defaultProperties": [DATA, LAYOUT],
        "properties": {
            DATA: {
                "type": "array",
                "description": "list of graphs to be plotted on a single plot",
                TITLE: "Data",
                MIN_ITEMS: 1,
                OPTIONS: {DISABLE_COLLAPSE: True},
                "items": {
                    "type": "object",
                    "title": "Data Dictionary",
                    OPTIONS: {DISABLE_COLLAPSE: True},
                    "required": ["type"],
                    "properties": {
                        "type": {
                            "type": "string",
                            TITLE: "Render Mode",
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
                            OPTIONS: {HIDDEN: True},
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
                            TYPE: "string",
                            TITLE: "Data on Y Axis",
                            ENUM: column_names,
                        },
                        ERROR_X: {
                            TYPE: "object",
                            "properties": {
                                ARRAY: {
                                    "type": "string",
                                    TITLE: "Data column to use for error bars",
                                    ENUM: column_names,
                                },
                            },
                            TITLE: "Symmetric error bars in the Y axis",
                        },
                        ERROR_Y: {
                            TYPE: "object",
                            "properties": {
                                ARRAY: {
                                    "type": "string",
                                    TITLE: "Data column to use for error bars",
                                    ENUM: column_names,
                                },
                            },
                            TITLE: "Symmetric error bars in the Y axis",
                        },
                        ERROR_Z: {
                            TYPE: "object",
                            "properties": {
                                ARRAY: {
                                    "type": "string",
                                    TITLE: "Data column to use for error bars",
                                    ENUM: column_names,
                                },
                            },
                            TITLE: "Symmetric error bars in the Z axis",
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
                        "opacity": {
                            "type": "number",
                            TITLE: "Opacity",
                            "minimum": 0,
                            "maximum": 1,
                        },
                    },
                },
            },
            LAYOUT: {
                "title": "Graph Layout",
                "description": "Determines how the graph looks (optional)",
                "type": "object",
                OPTIONS: {DISABLE_COLLAPSE: True, REMOVE_EMPTY_PROPERTIES: True},
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
                    "barmode": {
                        "type": "string",
                        "enum": ["stack", "group", "overlay", "relative"],
                    },
                    "shapes": {
                        TYPE: ARRAY,
                        ITEMS: {
                            "type": "object",
                            "title": "Shape Dictionary",
                            REQUIRED: ["type", "x0", "y0", "x1", "y1"],
                            PROPERTIES: {
                                "type": {
                                    TYPE: "string",
                                    "enum": ["line", "rect", "circle", "path",],
                                },
                                "layer": {TYPE: "string", "enum": ["above", "below",],},
                                "xref": {TYPE: "string", "enum": [X, "paper"]},
                                "yref": {TYPE: "string", "enum": [Y, "paper"]},
                                "x0": {TYPE: "number"},
                                "x1": {TYPE: "number"},
                                "y0": {TYPE: "number"},
                                "y1": {TYPE: "number"},
                                "line": {
                                    TYPE: "object",
                                    PROPERTIES: {
                                        "color": {
                                            TYPE: "string",
                                            ENUM: COLORS,
                                            "options": {"enum_titles": COLOR_NAMES},
                                        },
                                        "width": {
                                            TYPE: "number",
                                            "default": 2,
                                            "minimum": 0,
                                        },
                                        "dash": {
                                            TYPE: "string",
                                            ENUM: [
                                                "solid",
                                                "dot",
                                                "dash",
                                                "longdash",
                                                "dashdot",
                                                "longdashdot",
                                            ],
                                        },
                                    },
                                },
                                "fillcolor": {
                                    TYPE: "string",
                                    ENUM: ["#ffffff"] + COLORS,
                                    "options": {"enum_titles": ["white"] + COLOR_NAMES},
                                },
                            },
                        },
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
                TYPE: "To show more than one box in the plot, "
                'set "group by" in visualization options below',
            },
        },
        VIOLIN: {
            ENUM: [VIOLIN],
            REQUIRED: [TYPE, Y],
            DESCRIPTION: {
                TYPE: "To show more than one violin in the plot, "
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
        if len(directions[ENUM]) > 1:
            plot_schema[PROPERTIES][DATA][ITEMS][PROPERTIES][TYPE][OPTIONS][
                HIDDEN
            ] = False
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
