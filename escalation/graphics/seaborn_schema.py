# Copyright [2021] [Two Six Labs, LLC],
# Licensed under the Apache License, Version 2.0,

"""
There is no schema for seaborn available.
Build one by parsing the Seaborn code docstrings using NumpyDocString (which covers the Seaborn documentation formatting)
"""

from collections import defaultdict
import inspect
import re
import seaborn as sns
from numpydoc.docscrape import NumpyDocString

from utility.constants import *
from graphics.graphic_schema import GraphicsConfigInterfaceBuilder

X = "x"
Y = "y"
Z = "z"

# these are the plot types that don't require function calls on the data, and don't have
# dot-separated function names (which we haven't checked yet
SUPPORTED_PLOTS = [
    {GRAPHIC_NAME: "Scatter Plot", VALUE: "scatterplot"},
    {GRAPHIC_NAME: "Line Plot", VALUE: "lineplot"},
    # {GRAPHIC_NAME: "Relational Plot", VALUE: "relplot"},
    {GRAPHIC_NAME: "Histogram Plot", VALUE: "histplot"},
    {GRAPHIC_NAME: "Kernel Density Estimate Plot", VALUE: "kdeplot"},
    {
        GRAPHIC_NAME: "Empirical Cumulative Distribution Function Plot",
        VALUE: "ecdfplot",
    },
    # {GRAPHIC_NAME: "Distribution Plot", VALUE: "displot"},
    # {GRAPHIC_NAME: "Rug Plot", VALUE: "rugplot"},
    {GRAPHIC_NAME: "Strip Plot", VALUE: "stripplot"},
    {GRAPHIC_NAME: "Beeswarm Plot", VALUE: "swarmplot"},
    {GRAPHIC_NAME: "Box Plot", VALUE: "boxplot"},
    {GRAPHIC_NAME: "Violin Plot", VALUE: "violinplot"},
    {GRAPHIC_NAME: "Enhanced Box Plot", VALUE: "boxenplot"},
    {GRAPHIC_NAME: "Point Plot", VALUE: "pointplot"},
    {GRAPHIC_NAME: "Bar Plot", VALUE: "barplot"},
    {GRAPHIC_NAME: "Count Plot", VALUE: "countplot"},
    # {GRAPHIC_NAME: "Categorical Plot", VALUE: "catplot"},
    # {GRAPHIC_NAME: "Data and Regression Model Fit Plot (lmplot)", VALUE: "lmplot"},
    # {GRAPHIC_NAME: "Data and a Linear Regression Model Fit Plot", VALUE: "regplot"},
    # {GRAPHIC_NAME: "Residuals of a Linear Regression Plot", VALUE: "residplot"},
    # {GRAPHIC_NAME: "Heat Map", VALUE: "heatmap"},
    # {GRAPHIC_NAME: "Hierarchically-Clustered Heat Map Plot", VALUE: "clustermap"},
    # {GRAPHIC_NAME: "Pairwise Relationships Plot", VALUE: "pairplot"},
    # {GRAPHIC_NAME: "Joint Distribution Plot", VALUE: "jointplot"},
]

# these are implemented in seaborn as classes, and need slightly different treatment
SUPPORTED_PLOT_CLASSES = [
    "FacetGrid",  # i
    "PairGrid",
    "JointGrid",
]

WIZARD_CUSTOMIZATION = {
    "scatterplot": {REQUIRED: ["x", "y"]},
    "lineplot": {REQUIRED: ["x", "y"]},
    # "relplot": {
    #    REQUIRED: ["x", "y", "kind", "col"],
    #    ENUM: {"kind": ["scatter", "line"]},
    # },
    "histplot": {REQUIRED: ["x"]},
    "kdeplot": {REQUIRED: ["x"]},
    "ecdfplot": {REQUIRED: ["x"]},
    # "displot": {
    #    REQUIRED: ["x", "kind", "col"],
    #    ENUM: {"kind": ["hist", "kde", "ecdf"]},
    # },
    "stripplot": {REQUIRED: ["x", "y"]},
    "swarmplot": {REQUIRED: ["x", "y"]},
    "boxplot": {REQUIRED: ["y"]},
    "violinplot": {REQUIRED: ["y"]},
    "boxenplot": {REQUIRED: ["y"]},
    "pointplot": {REQUIRED: ["x", "y"]},
    "barplot": {REQUIRED: ["x", "y"]},
    "countplot": {REQUIRED: ["x"]},
    # "catplot": {
    #    REQUIRED: ["x", "y", "kind", "col"],
    #    ENUM: {
    #        "kind": [
    #            "strip",
    #            "swarm",
    #            "box",
    #            "violin",
    #            "boxen",
    #            "point",
    #            "bar",
    #            "count",
    #        ]
    #    },
    # },
    # "regplot": {REQUIRED: ["x", "y"]},
    # "residplot": {REQUIRED: ["x", "y"]},
    # "heatmap": {REQUIRED: []},
    # "clustermap": {REQUIRED: []},
}


class SeabornGraphicSchema(GraphicsConfigInterfaceBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_individual_plot_type_schema(self, plot_name):
        plot_function = getattr(sns, plot_name)
        plot_function_signature = inspect.signature(plot_function).parameters
        doc_object = NumpyDocString(plot_function.__doc__)
        doc = build_docstring_with_separated_keys(doc_object)
        # with open(os.path.join("graphics", "seaborn_schemas", f"{plot_name}_seaborn_schema.json"), 'w') as fout:
        template_schema = get_seaborn_single_plot_schema_template(plot_name)
        for param in plot_function_signature.keys():
            configurable_param_type = configurable_params.get(param)
            # not whitelisted in schema for inclusion in configuration
            if not configurable_param_type:
                continue
            param_dict = {}
            if isinstance(configurable_param_type, list):
                # all of our enumerated types are strings
                param_dict[TYPE] = STRING
                param_dict[ENUM] = configurable_param_type
            elif (
                isinstance(configurable_param_type, str)
                and configurable_param_type == COLUMN_NAMES
            ):
                param_dict[TYPE] = STRING
                if self.data_holder.possible_column_names:
                    param_dict[ENUM] = self.data_holder.possible_column_names
            else:
                param_dict[TYPE] = configurable_param_type
            try:
                param_dict[DESCRIPTION] = doc[param]
            except:
                # print(f"{param} not found in docstring for {plot_name}, not including")
                continue
            param_dict[TITLE] = param
            # todo: check docstring if optional and collapse
            # param_dict[DESCRIPTION][OPTIONS] = {HIDDEN: True},
            template_schema[PROPERTIES][DATA][ITEMS][PROPERTIES][param] = param_dict
        plot_specific_customization = WIZARD_CUSTOMIZATION[plot_name]
        enum_dict = plot_specific_customization.get(ENUM, {})
        for param, enum_elements in enum_dict.items():
            template_schema[PROPERTIES][DATA][ITEMS][PROPERTIES][param][
                ENUM
            ] = enum_elements
        template_schema[PROPERTIES][DATA][ITEMS][
            REQUIRED
        ] += plot_specific_customization[REQUIRED]
        return template_schema

    @staticmethod
    def get_available_plots():
        return SUPPORTED_PLOTS


def get_seaborn_single_plot_schema_template(plot_name):
    schema = {
        "$schema": "http://json-schema.org/draft/2019-09/schema#",
        "title": "Seaborn Graph Config",
        "description": "Assembles graphs according to Seaborn definitions",
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
                MAX_ITEMS: 1,
                OPTIONS: {DISABLE_COLLAPSE: True},
                "items": {
                    TYPE: "object",
                    TITLE: "Data Dictionary",
                    OPTIONS: {DISABLE_COLLAPSE: True},
                    REQUIRED: ["type"],
                    PROPERTIES: {
                        "type": {
                            "type": "string",
                            TITLE: "Render Mode",
                            "enum": [plot_name],
                            OPTIONS: {HIDDEN: True},
                        },
                    },
                },
            },
            LAYOUT: {
                "title": "Graph Layout",
                DESCRIPTION: "Determines how the graph looks (optional)",
                "type": "object",
                OPTIONS: {DISABLE_COLLAPSE: True, REMOVE_EMPTY_PROPERTIES: True},
                PROPERTIES: {
                    FIGSIZE: {
                        TYPE: ARRAY_STRING,
                        TITLE: "Figure Size",
                        DESCRIPTION: "Width, height in inches. "
                        "Determines the size of the image when downloaded"
                        " and the aspect ratio when shown in the browser.",
                        MIN_ITEMS: 2,
                        MAX_ITEMS: 2,
                        ITEMS: [
                            {
                                TYPE: NUMBER,
                                TITLE: "Width, coord",
                                MINIMUM: 0,
                                DEFAULT: 8,
                            },
                            {
                                TYPE: NUMBER,
                                TITLE: "Height, coord",
                                MINIMUM: 0,
                                DEFAULT: 6,
                            },
                        ],
                    }
                },
            },
        },
    }
    return schema


configurable_params = dict(
    [
        ("x", COLUMN_NAMES),  # column_names
        ("y", COLUMN_NAMES),  # column_names
        ("hue", COLUMN_NAMES),  # column_names
        ("palette", STRING),
        ("hue_order", ARRAY_STRING),  # ARRAY_STRING of string values in a column
        ("color", STRING),
        ("order", ARRAY_STRING),  # ARRAY_STRING of string values in a column
        ("legend", ["auto", "brief", "full", False]),
        ("hue_norm", ARRAY_STRING),
        ("orient", ["v", "h"]),
        ("units", COLUMN_NAMES),  # column_names
        ("dodge", BOOLEAN),
        ("size", COLUMN_NAMES),  # column_names
        ("height", NUMBER),
        ("ci", INTEGER),
        ("n_boot", INTEGER),
        ("markers", STRING),
        ("seed", INTEGER),
        ("kind", STRING),  # todo: enum?
        ("aspect", NUMBER),
        # ("estimator", 5),
        ("linewidth", NUMBER),
        ("saturation", NUMBER),
        ("row", COLUMN_NAMES),
        ("col", COLUMN_NAMES),
        ("col_wrap", INTEGER),
        ("row_order", ARRAY_STRING),  # ARRAY_STRING of string values in a column
        ("col_order", ARRAY_STRING),  # ARRAY_STRING of string values in a column
        ("weights", COLUMN_NAMES),  # column_names
        (
            "log_scale",
            BOOLEAN,
        ),  # can also be a number defining log scale, or a pair for both axes
        # ("line_kws", 4),
        # ("cbar_kws", 4),
        ("robust", BOOLEAN),
        ("dropna", BOOLEAN),
        ("style", STRING),
        # ("sizes", 3), ("size_order", 3), ("size_norm", 3), ("style_order", 3), used when specifying ARRAYs corresponding to values
        # ("facet_kws", 3),
        ("x_bins", INTEGER),
        ("x_jitter", NUMBER),
        ("y_jitter", NUMBER),
        ("cbar", BOOLEAN),
        # ("cbar_ax", 3), # check: this should be applied to current graph ax only
        ("width", NUMBER),
        ("scale", [None, "area", "count", "width"]),
        ("lowess", BOOLEAN),
        ("x_partial", STRING),
        ("y_partial", STRING),
        # ("scatter_kws", 3),
        ("dashes", BOOLEAN),
        ("stat", ["count", "frequency", "density", "probability"]),
        ("cumulative", BOOLEAN),
        ("common_norm", BOOLEAN),
        ("multiple", ["layer", "dodge", "stack", "fill"]),
        ("fill", BOOLEAN),
        ("thresh", NUMBER),
        # ("bw", [‘scott’, ‘silverman’, NUMBER]),
        ("gridsize", INTEGER),
        ("cut", NUMBER),
        ("legend_out", BOOLEAN),
        ("sharex", BOOLEAN),
        ("sharey", BOOLEAN),
        ("edgecolor", STRING),
        ("errwidth", NUMBER),
        ("capsize", NUMBER),
        # ("x_estimator", 2),
        # ("x_ci", 2),
        ("scatter", BOOLEAN),
        ("fit_reg", BOOLEAN),
        ("logistic", BOOLEAN),
        ("logx", BOOLEAN),
        ("truncate", BOOLEAN),
        ("label", STRING),
        # ("mask", 2),
        ("y_bins", INTEGER),
        ("alpha", NUMBER),
        ("sort", None),
        ("err_style", None),
        # ("err_kws", None),
        ("rug", None),
        # ("rug_kws", None),
        ("bins", None),
        ("binwidth", None),
        ("binrange", None),
        ("discrete", None),
        ("common_bins", BOOLEAN),
        ("element", None),
        ("shrink", None),
        ("kde", None),
        # ("kde_kws", None),
        ("pthresh", None),
        ("pmax", None),
        ("shade", None),
        ("vertical", None),
        ("kernel", None),
        ("clip", None),
        ("shade_lowest", None),
        ("common_grid", None),
        ("levels", None),
        ("bw_method", None),
        ("bw_adjust", None),
        ("data2", None),
        ("complementary", None),
        ("axis", None),
        ("expand_margins", None),
        ("a", None),
        ("margin_titles", None),
        ("jitter", None),
        ("fliersize", None),
        ("whis", None),
        ("scale_hue", None),
        ("inner", None),
        ("split", None),
        ("k_depth", None),
        ("outlier_prop", None),
        ("trust_alpha", None),
        ("showfliers", None),
        ("linestyles", None),
        ("join", None),
        ("errcolor", None),
        ("marker", None),
        ("vmin", None),
        ("vmax", None),
        ("cmap", None),
        ("center", None),
        ("annot", None),
        ("fmt", None),
        # ("annot_kws", None),
        ("linewidths", NUMBER),
        ("linecolor", STRING),  # enum matplotlib color codes with optional user entry
        ("square", None),
        ("xticklabels", None),
        ("yticklabels", None),
        # ("pivot_kws", None),
        ("method", None),
        ("metric", None),
        ("z_score", None),
        ("standard_scale", None),
        ("figsize", None),
        ("row_cluster", None),
        ("col_cluster", None),
        ("row_linkage", None),
        ("col_linkage", None),
        ("row_colors", None),
        ("col_colors", None),
        ("dendrogram_ratio", None),
        ("colors_ratio", None),
        ("cbar_pos", None),
        # ("tree_kws", None),
        ("vars", None),
        ("x_vars", None),
        ("y_vars", None),
        ("diag_kind", None),
        ("corner", None),
        # ("plot_kws", None),
        # ("diag_kws", None),
        # ("grid_kws", None),
        ("ratio", None),
        ("space", None),
        ("xlim", ARRAY_STRING),
        ("ylim", ARRAY_STRING),
        ("marginal_ticks", None),
        # ("joint_kws", None),
        # ("marginal_kws", None),
    ]
)


def build_docstring_with_separated_keys(numpy_doc):
    """
    the docstrings are written with some params combined. break them up
    :param numpy_doc: NumpyDocString instance
    :return: dict
    """
    docs_dict = {}
    expandable_variable_regex = r"\{(.+)\}(.+)"
    for param in numpy_doc["Parameters"]:
        groups = re.match(expandable_variable_regex, param.name)
        if groups:
            # make params in form {x, y}_bins into x_bins and y_bins params
            split_params = [x + groups[2] for x in groups[1]]
        else:
            split_params = [x.strip() for x in param.name.split(",")]
        for param_name in split_params:
            docs_dict[param_name] = param.desc
    return docs_dict


# todo: plot classes in schema
# for plot_name in SUPPORTED_PLOT_CLASSES:
#     print(f"\n{plot_name}")
#     plot_class = getattr(sns, plot_name)
#     plot_function = plot_class.__init__
#     doc = NumpyDocString(plot_function.__doc__)
#     print(doc["Parameters"][0])
