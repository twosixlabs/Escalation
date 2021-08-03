# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import copy
import json

from graphics.graphic_schema import GraphicsConfigInterfaceBuilder
from utility.constants import *
from utility.helper_classes import NestedDict
from utility.schema_utils import conditional_dict

MODE = "mode"


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


SUPPORTED_PLOTS = [
    {GRAPHIC_NAME: "Scatter or Line Plot", VALUE: SCATTER},
    {GRAPHIC_NAME: "Bar Plot", VALUE: BAR},
    # {GRAPHIC_NAME: "Heat Map", VALUE: HEATMAP},
    # {GRAPHIC_NAME: "Contour Plot", VALUE: CONTOUR},
    {GRAPHIC_NAME: "Box Plot", VALUE: BOX},
    {GRAPHIC_NAME: "Violin Plot", VALUE: VIOLIN},
    {GRAPHIC_NAME: "Histogram", VALUE: HISTOGRAM},
    {GRAPHIC_NAME: "2D Histogram", VALUE: HISTOGRAM2D},
    {GRAPHIC_NAME: "3D Scatter or Line Plot", VALUE: SCATTER3D},
    {GRAPHIC_NAME: "3D Mesh Plot", VALUE: MESH3D},
    {GRAPHIC_NAME: "Geographical Scatter", VALUE: SCATTERGEO,},
    {GRAPHIC_NAME: "Mapbox Scatter", VALUE: SCATTERMAPBOX},
]

COLUMN_OPTION_DICT = {
    SCATTERGEO: [
        [PROPERTIES, DATA, ITEMS, PROPERTIES, MARKER, PROPERTIES, "size"],
        [PROPERTIES, DATA, ITEMS, PROPERTIES, MARKER, PROPERTIES, "color"],
    ],
    SCATTERMAPBOX: [
        [PROPERTIES, DATA, ITEMS, PROPERTIES, MARKER, PROPERTIES, "size"],
        [PROPERTIES, DATA, ITEMS, PROPERTIES, MARKER, PROPERTIES, "color"],
    ],
}


class PlotlyGraphicSchema(GraphicsConfigInterfaceBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_generic_plotly_plot_schema_template(self):
        schema = {
            "$schema": "http://json-schema.org/draft/2019-09/schema#",
            "title": "Plotly Graph Config",
            "description": "dictionary that follows https://plotly.com/javascript/reference/",
            "type": "object",
            "required": [DATA],
            OPTIONS: {DISABLE_COLLAPSE: True, REMOVE_EMPTY_PROPERTIES: True},
            "defaultProperties": [DATA, LAYOUT],
            PROPERTIES: {
                DATA: {
                    "type": "array",
                    "description": "list of graphs to be plotted on a single plot",
                    TITLE: "Data",
                    MIN_ITEMS: 1,
                    OPTIONS: {DISABLE_COLLAPSE: True},
                    ITEMS: {
                        TYPE: "object",
                        "title": "Data Dictionary",
                        OPTIONS: {DISABLE_COLLAPSE: True},
                        "required": ["type"],
                        PROPERTIES: {
                            TYPE: {
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
                                    SCATTERGEO,
                                    SCATTERMAPBOX,
                                ],
                                OPTIONS: {HIDDEN: True},
                            },
                            X: {
                                "type": "string",
                                TITLE: "Data on X Axis",
                                **conditional_dict(
                                    ENUM, self.data_holder.possible_column_names
                                ),
                            },
                            Y: {
                                "type": "string",
                                TITLE: "Data on Y Axis",
                                **conditional_dict(
                                    ENUM, self.data_holder.possible_column_names
                                ),
                            },
                            Z: {
                                TYPE: "string",
                                TITLE: "Data on Z Axis",
                                **conditional_dict(
                                    ENUM, self.data_holder.possible_column_names
                                ),
                            },
                            ERROR_X: {
                                TYPE: "object",
                                "properties": {
                                    ARRAY_STRING: {
                                        "type": "string",
                                        TITLE: "Data column to use for error bars",
                                        **conditional_dict(
                                            ENUM, self.data_holder.possible_column_names
                                        ),
                                    },
                                },
                                TITLE: "Symmetric error bars in the X axis",
                            },
                            ERROR_Y: {
                                TYPE: "object",
                                "properties": {
                                    ARRAY_STRING: {
                                        "type": "string",
                                        TITLE: "Data column to use for error bars",
                                        **conditional_dict(
                                            ENUM, self.data_holder.possible_column_names
                                        ),
                                    },
                                },
                                TITLE: "Symmetric error bars in the Y axis",
                            },
                            ERROR_Z: {
                                TYPE: "object",
                                "properties": {
                                    ARRAY_STRING: {
                                        "type": "string",
                                        TITLE: "Data column to use for error bars",
                                        **conditional_dict(
                                            ENUM, self.data_holder.possible_column_names
                                        ),
                                    },
                                },
                                TITLE: "Symmetric error bars in the Z axis",
                            },
                            LATITUDE: {
                                TYPE: "string",
                                TITLE: "Data column with latitude values",
                                **conditional_dict(
                                    ENUM, self.data_holder.possible_column_names
                                ),
                            },
                            LONGITUDE: {
                                TYPE: "string",
                                TITLE: "Data column with longitude values",
                                **conditional_dict(
                                    ENUM, self.data_holder.possible_column_names
                                ),
                            },
                            HOVERTEXT: {
                                DESCRIPTION: "Differs from the plotly documentation."
                                " Takes in list of column names, where the data in each columns is shown for "
                                "the data point on hover. (a default hovertemplate is set so the user does not has to"
                                " set one)."
                                " To be seen, trace `hoverinfo` must contain a *text* flag (which it does by default).",
                                TYPE: "array",
                                OPTIONS: {DISABLE_COLLAPSE: True},
                                "items": {
                                    "type": "string",
                                    TITLE: "Column Name",
                                    **conditional_dict(
                                        ENUM, self.data_holder.possible_column_names
                                    ),
                                },
                            },
                            MODE: {
                                TYPE: "string",
                                TITLE: "Graph Style",
                                DESCRIPTION: "Determines the drawing mode for this scatter trace. If the selected option "
                                "includes *text* then the `text` elements appear at the coordinates."
                                " Otherwise, the `text` elements appear on hover",
                                ENUM: [
                                    "markers",
                                    "lines",
                                    "text",
                                    "lines+markers",
                                    "markers+text",
                                    "lines+text",
                                    "lines+markers+text",
                                    "none",
                                ],
                            },
                            TRANSFORMS: {
                                DESCRIPTION: "Transforms on the data. This differs from plotly's schema a little bit."
                                "Here, transforms is a dictionary with keys 'groupby' and 'aggreations'"
                                " instead"
                                " of a list dictionaries where the transform is specified by the type key."
                                " For filters use the data selector dictionary.",
                                TYPE: OBJECT,
                                OPTIONS: {
                                    DISABLE_COLLAPSE: True,
                                    REMOVE_EMPTY_PROPERTIES: True,
                                },
                                PROPERTIES: {
                                    GROUPBY: {
                                        "type": OBJECT,
                                        "description": "Group by transform of the data",
                                        "id": "groupby_id",
                                        "required": [GROUPS],
                                        PROPERTIES: {
                                            "enabled": {
                                                TYPE: BOOLEAN,
                                                DEFAULT: True,
                                                DESCRIPTION: "Determines whether the transform is enabled or disabled.",
                                            },
                                            "nameformat": {
                                                TYPE: STRING,
                                                DESCRIPTION: "Pattern by which grouped traces are named."
                                                " If only one trace is"
                                                ' present, defaults to the group name (`"%{group}"`), otherwise'
                                                " defaults to the group name with trace name "
                                                '(`"%{group} (%{trace})"`). Available escape sequences are'
                                                " `%{group}`, which inserts the group name, and `%{trace}`, which"
                                                " inserts the trace name. If grouping GDP data by country when more"
                                                " than one trace is present, for example, the default"
                                                ' "%{group} (%{trace})" would return "Monaco (GDP per capita)".',
                                            },
                                            GROUPS: {
                                                TYPE: "array",
                                                TITLE: "Groups",
                                                DESCRIPTION: "Sets the groups in which the trace data will be split."
                                                " For example, with `x` set to *[1, 2, 3, 4]* and `groups` set to"
                                                " *['a', 'b', 'a', 'b']*,"
                                                " the groupby transform with split in one trace with `x` [1, 3] and one"
                                                " trace with `x` [2, 4]."
                                                " Multiple data columns means the group will be the concatenation"
                                                " of all the rows.",
                                                OPTIONS: {DISABLE_COLLAPSE: True},
                                                "items": {
                                                    "type": "string",
                                                    TITLE: "Column Name",
                                                    **conditional_dict(
                                                        ENUM,
                                                        self.data_holder.filter_dict[
                                                            FILTER
                                                        ],
                                                        [NO_GROUP_BY],
                                                    ),
                                                },
                                            },
                                            "Styles": {
                                                TYPE: "array",
                                                TITLE: "Styles",
                                                DESCRIPTION: "Sets each group styles. For example, with `groups` set "
                                                "to *['a', 'b', 'a', 'b']* and `styles` set to "
                                                "*[{target: 'a', value: { marker: { color: 'red' } }}]* marker points"
                                                " in group *'a'* will be drawn in red. "
                                                "Only use if specifying a single column to group by.",
                                                ITEMS: {
                                                    TITLE: "Style Dictionary",
                                                    TYPE: OBJECT,
                                                    PROPERTIES: {
                                                        "target": {
                                                            TYPE: "string",
                                                            DESCRIPTION: "Value of data in column",
                                                            # watch will call the functions in enumSource (default_selected_filter,
                                                            # identity_callback; defined in the JS) whenever COLUMN_NAME is changed,
                                                            # it will also store the value of COLUMN_NAME to a variable called COLUMN_NAME
                                                            #  to be used by the JS
                                                            **(
                                                                {
                                                                    "watch": {
                                                                        GROUPS: ".".join(
                                                                            [
                                                                                "groupby_id",
                                                                                GROUPS,
                                                                            ]
                                                                        ),
                                                                    },
                                                                    "enumSource": [
                                                                        {
                                                                            "source": self.data_holder.unique_entry_values_list,
                                                                            "filter": COLUMN_VALUE_FILTER,
                                                                            "title": CALLBACK,
                                                                            "value": CALLBACK,
                                                                        }
                                                                    ],
                                                                }
                                                                if self.data_holder.unique_entry_values_list
                                                                else {}
                                                            ),
                                                        },
                                                        "value": {
                                                            TYPE: "object",
                                                            PROPERTIES: {
                                                                "marker": {
                                                                    TYPE: "object",
                                                                    PROPERTIES: {
                                                                        "color": {
                                                                            TYPE: "string"
                                                                        }
                                                                    },
                                                                }
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                            USER_SELECTABLE_OPTIONS: {
                                                TYPE: "array",
                                                TITLE: "Interactive Group By Selector",
                                                DESCRIPTION: "A non-empty array will allow a user to"
                                                "change the group by of the visualization on the dashboard. The "
                                                "elements of the array specify columns available to the user.",
                                                OPTIONS: {DISABLE_COLLAPSE: True},
                                                "items": {
                                                    "type": "string",
                                                    TITLE: "Column Name",
                                                    **conditional_dict(
                                                        ENUM,
                                                        self.data_holder.filter_dict[
                                                            FILTER
                                                        ],
                                                    ),
                                                },
                                            },
                                        },
                                    },
                                    AGGREGATE: {
                                        TYPE: ARRAY_STRING,
                                        DESCRIPTION: "Performs aggregations on the data",
                                        ITEMS: {
                                            TYPE: OBJECT,
                                            REQUIRED: [GROUPS, AGGREGATIONS],
                                            PROPERTIES: {
                                                "enabled": {
                                                    TYPE: BOOLEAN,
                                                    DEFAULT: True,
                                                    DESCRIPTION: "Determines whether the transform is enabled or disabled.",
                                                },
                                                GROUPS: {
                                                    TYPE: "array",
                                                    TITLE: "Groups",
                                                    DESCRIPTION: "Sets the grouping target to which the aggregation is"
                                                    " applied. Data points with matching group values will be coalesced"
                                                    " into one point, using the supplied aggregation functions to reduce"
                                                    " data in other data arrays. If a string, `groups` is assumed"
                                                    " to be a reference to a data array in the parent trace"
                                                    " object. To aggregate by nested variables, use *.* to"
                                                    " access them. For example, set `groups` to *marker.color* to aggregate"
                                                    " about the marker color array. If an array, `groups` is itself the "
                                                    "data array by which we aggregate."
                                                    " Multiple data columns means the group will be the "
                                                    "concatenation of all the rows.",
                                                    OPTIONS: {DISABLE_COLLAPSE: True},
                                                    "items": {
                                                        "type": "string",
                                                        TITLE: "Column Name",
                                                        **conditional_dict(
                                                            ENUM,
                                                            self.data_holder.possible_column_names,
                                                        ),
                                                    },
                                                },
                                                AGGREGATIONS: {
                                                    "type": ARRAY_STRING,
                                                    TITLE: "Aggregations",
                                                    OPTIONS: {DISABLE_COLLAPSE: True},
                                                    ITEMS: {
                                                        TYPE: OBJECT,
                                                        TITLE: "Aggregation",
                                                        REQUIRED: [TARGET, "func"],
                                                        PROPERTIES: {
                                                            TARGET: {
                                                                TYPE: STRING,
                                                                DESCRIPTION: "A reference to the data array in the parent trace to"
                                                                " aggregate. To aggregate by nested variables, use *.*"
                                                                " to access them. For example, set `groups` to"
                                                                " *marker.color* to aggregate over the marker color array."
                                                                " The referenced array must already exist, unless `func`"
                                                                " is *count*, and each array may only be referenced once.",
                                                            },
                                                            "func": {
                                                                TYPE: STRING,
                                                                DESCRIPTION: "Sets the aggregation function. All values from the linked"
                                                                " `target`, corresponding to the same value in the"
                                                                " `groups` array, are collected and reduced by "
                                                                "this function. "
                                                                "*count* is simply the number of values in the `groups` "
                                                                "array, so does not even require the linked array "
                                                                "to exist."
                                                                " *first* (*last*) is just the first (last) linked value. "
                                                                "Invalid values are ignored, so for example in *avg* they"
                                                                " do not contribute to either the numerator or the"
                                                                " denominator. Any data type (numeric, date, category)"
                                                                " may be aggregated with any function, even though in"
                                                                " certain cases it is unlikely to make sense, for example"
                                                                " a sum of dates or average of categories. *median* will"
                                                                " return the average of the two central values if there"
                                                                " is an even count. *mode* will return the first value"
                                                                " to reach the maximum count, in case of a tie."
                                                                " *change* will return the difference between the first"
                                                                " and last linked values. *range* will return the"
                                                                " difference between the min and max linked values.",
                                                                ENUM: [
                                                                    "avg",
                                                                    "sum",
                                                                    "min",
                                                                    "max",
                                                                    "mode",
                                                                    "median",
                                                                    "count",
                                                                    "stddev",
                                                                    "first",
                                                                    "last",
                                                                ],
                                                            },
                                                            "funcmode": {
                                                                TYPE: STRING,
                                                                ENUM: [
                                                                    "sample",
                                                                    "population",
                                                                ],
                                                                DEFAULT: "sample",
                                                                DESCRIPTION: "*stddev* supports two formula variants: *sample*"
                                                                " (normalize by N-1) and *population* (normalize by N).",
                                                            },
                                                            "enabled": {
                                                                TYPE: BOOLEAN,
                                                                "valType": "boolean",
                                                                DEFAULT: True,
                                                                "editType": "calc",
                                                                DESCRIPTION: "Determines whether this aggregation function"
                                                                " is enabled or disabled.",
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                LAYOUT: {
                    "title": "Graph Layout",
                    DESCRIPTION: "Determines how the graph looks (optional)",
                    "type": "object",
                    OPTIONS: {DISABLE_COLLAPSE: True, REMOVE_EMPTY_PROPERTIES: True},
                },
            },
        }
        return schema

    def build_individual_plot_type_schema(self, plot_type):
        """
        Seperate schemas for each plot
        :return: dict_of_schemas, schema_to_type
        """
        # If the element is not in required we will delete it
        programmed_data_options = [TYPE, X, Y, Z, MODE, LATITUDE, LONGITUDE]

        directions_for_building_schemas = {
            SCATTER: {
                ENUM: [SCATTERGL, SCATTER],
                REQUIRED: [TYPE, X, Y, MODE],
                DESCRIPTION: {
                    TYPE: "scattergl uses uses WebGL which is faster for lots of points"
                },
            },
            BAR: {ENUM: [BAR], REQUIRED: [TYPE, X, Y],},
            BOX: {ENUM: [BOX], REQUIRED: [TYPE, X, Y],},
            VIOLIN: {ENUM: [VIOLIN], REQUIRED: [TYPE, X, Y],},
            HISTOGRAM: {ENUM: [HISTOGRAM], REQUIRED: [TYPE, X],},
            CONTOUR: {ENUM: [CONTOUR], REQUIRED: [TYPE, X, Y, Z],},
            HISTOGRAM2D: {
                ENUM: [HISTOGRAM2D, HISTOGRAM2DCONTOUR],
                REQUIRED: [TYPE, X, Y],
            },
            MESH3D: {ENUM: [MESH3D], REQUIRED: [TYPE, X, Y, Z],},
            HEATMAP: {
                ENUM: [HEATMAPGL, HEATMAP],
                REQUIRED: [TYPE, X, Y, Z],
                DESCRIPTION: {
                    TYPE: "heatmapgl uses WebGL which may be faster for lots of points"
                },
            },
            SCATTER3D: {ENUM: [SCATTER3D], REQUIRED: [TYPE, X, Y, Z, MODE],},
            SCATTERGEO: {
                ENUM: [SCATTERGEO],
                REQUIRED: [TYPE, LATITUDE, LONGITUDE, MODE],
            },
            SCATTERMAPBOX: {
                ENUM: [SCATTERMAPBOX],
                REQUIRED: [TYPE, LATITUDE, LONGITUDE, MODE],
            },
        }

        plot_schema = self.build_generic_plotly_plot_schema_template()

        # populate the layout dictionary with the plotly api
        with open("plotly_api/layout_plotly_schema.json", "r") as file:
            plotly_layout_schema = json.load(file)
        plot_schema[PROPERTIES][LAYOUT][PROPERTIES] = plotly_layout_schema[PROPERTIES]
        directions = directions_for_building_schemas[plot_type]
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

        plot_schema = merge_with_plotly_api(plot_schema, plot_type)
        if plot_type in COLUMN_OPTION_DICT:
            plot_schema = self.add_column_name_as_option(
                plot_schema, COLUMN_OPTION_DICT[plot_type]
            )
        return plot_schema

    def build_data_filter_schema(self):
        selectable_data_schema = super().build_data_filter_schema()
        selectable_data_schema[PROPERTIES][GROUPBY] = {
            "type": "object",
            "title": "Group By Selector",
            "required": [ENTRIES],
            OPTIONS: {COLLAPSED: self.data_holder.collapse_dict[GROUPBY_SELECTOR]},
            "additionalProperties": False,
            PROPERTIES: {
                ENTRIES: {
                    "type": "array",
                    OPTIONS: {DISABLE_COLLAPSE: True},
                    TITLE: "Entries",
                    "items": {
                        "type": "string",
                        "enum": self.data_holder.filter_dict[FILTER],
                    },
                },
                "multiple": {"type": "boolean"},
                DEFAULT_SELECTED: {
                    "type": "array",
                    TITLE: "Default Selected",
                    "description": "optional, default filter, list of column values",
                    "items": {
                        "type": "string",
                        "enum": self.data_holder.filter_dict[FILTER],
                    },
                },
            },
        }
        return selectable_data_schema

    @staticmethod
    def get_available_plots():
        return SUPPORTED_PLOTS

    def add_column_name_as_option(self, plot_schema, paths):
        def add_column_names_to_schema(path):
            """
            Adds an option to pick from the list of column names in the database to the schema at path.
            Done inplace
            :param path:
            :return:
            """
            plot_schema_nested = NestedDict(plot_schema)
            child_dict = plot_schema_nested[path]
            new_dict = {DESCRIPTION: child_dict.pop(DESCRIPTION, ""), ANYOF: []}
            child_dict[TITLE] = child_dict[TYPE]
            new_dict[ANYOF].append(child_dict)
            new_dict[ANYOF].append(
                {
                    TYPE: "string",
                    TITLE: "Column Name",
                    **conditional_dict(ENUM, self.data_holder.possible_column_names),
                }
            )
            plot_schema_nested[path] = new_dict

        for cur_path in paths:
            add_column_names_to_schema(cur_path)
        return plot_schema


def merge_with_plotly_api(schema_dict: dict, plot_type: str) -> dict:
    """
    Take properties from the plotly api and merge them into the hand-defined schema. We
    manually specify some things we want to show in our wizard, but populate the rest
    by default
    :param schema_dict:
    :param plot_type:
    :return:
    """
    with open(f"plotly_api/{plot_type}_plotly_schema.json", "r") as file:
        plotly_schema = json.load(file)

    schema_property_dict = schema_dict[PROPERTIES][DATA][ITEMS][PROPERTIES]
    for property_key, property_info in plotly_schema[ATTRIBUTES].items():
        if property_key in schema_property_dict:
            continue
        schema_property_dict[property_key] = property_info
    schema_dict[PROPERTIES][DATA][ITEMS][PROPERTIES] = schema_property_dict
    # check for special layout properties with this type of plot
    if LAYOUT_ATTRIBUTES in plotly_schema:
        schema_dict[PROPERTIES][LAYOUT][PROPERTIES].update(
            plotly_schema[LAYOUT_ATTRIBUTES]
        )
    return schema_dict
