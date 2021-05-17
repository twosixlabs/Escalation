# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
"""
Note, avoiding Pyplot here because of this:
https://matplotlib.org/devdocs/gallery/user_interfaces/web_application_server_sgskip.html
'When using Matplotlib in a web server it is strongly recommended to not use pyplot (pyplot maintains references to the opened figures to make show work, but this will cause memory leaks unless the figures are properly closed).'

"""

import base64
import io
import json

from graphics.graphic_class import Graphic

from utility.constants import *

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import pandas as pd
import seaborn as sns

X = "x"
Y = "y"
Z = "z"
ERROR_X = "error_x"
ERROR_Y = "error_y"
ERROR_Z = "error_z"
POSSIBLE_AXIS = [X, Y, Z]
POSSIBLE_ERROR_AXES = [ERROR_X, ERROR_Y, ERROR_Z]


NROWS = "nrows"
NCOLS = "ncols"
SHAREX = "sharex"
SHAREY = "sharey"

DEFAULT_LAYOUT_OPTIONS = {
    NROWS: 1,
    NCOLS: 1,
    FIGSIZE: [8, 6],
    SHAREX: False,
    SHAREY: False,
}
# seaborn has a number of plot attributes that can be defined using a data column
# todo: how do we find these exhaustively?
PLOT_DATA_DEFINED_ATTRIBUTES = [
    "hue",
    "size",
    "style",
    "units",
    "weights",
    "row",
    "col",
]


# todo: Some args take list of column names, which we need to account for
# https://seaborn.pydata.org/generated/seaborn.pairplot.html?highlight=keys%20data
lists_of_keys = ["vars", "x_vars", "y_vars"]


# Several of the seaborn commands create their own figure automatically.
# This is hardcoded into the seaborn code, so there is currently no way to produce such plots into existing figure objects.
forbidden_plots = [
    "PairGrid",
    "FacetGrid",
    "JointGrid",
    "pairplot",
    "jointplot",
    "lmplot",
]


def create_seaborn_fig_from_data_and_definition(data, plot_options):
    # plot_options[LAYOUT] define figure level formatting:
    # figure size, number and arrangement of subplots, background, spines, axlabels
    # get user defined values, and update with default values
    layout_dict = plot_options.get(LAYOUT, {})
    for viz_key, default_value in DEFAULT_LAYOUT_OPTIONS.items():
        if viz_key not in layout_dict:
            layout_dict[viz_key] = default_value
    plot_options[LAYOUT] = layout_dict

    nrows = layout_dict[NROWS]
    ncols = layout_dict[NCOLS]
    fig = Figure(figsize=layout_dict[FIGSIZE])
    for ind in range(1, nrows * ncols + 1):
        fig.add_subplot(nrows, ncols, ind)

    fig.set_size_inches(layout_dict[FIGSIZE])
    for plot_ind, plot_definition in enumerate(plot_options["data"]):
        ax = fig.axes[plot_ind]
        # get the seaborn plotting function from the seaborn library based on the name
        plot_type = plot_definition.pop(TYPE)
        if plot_type in forbidden_plots:
            raise ValueError(f"{plot_type} not supported yet")
        plot_function = getattr(sns, plot_type)
        # separate out fig/ax parameters from seaborn function parameters
        g = plot_function(data=data, ax=ax, **plot_definition)
        # ax.legend(bbox_to_anchor=(1.1, 0.9), ncol=1)
        # g.legend(loc='center left', bbox_to_anchor=(1.1, 0.9), ncol=1)

    return fig


def get_canvas_for_rendering_in_html(fig):
    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)
    fig.savefig(output, format="png")
    output.seek(0)
    buffer = b"".join(output)
    buffer_64_encoded = base64.b64encode(buffer)

    seaborn_fig_bytes = buffer_64_encoded.decode("utf-8")
    return seaborn_fig_bytes


class SeabornPlot(Graphic):
    def make_dict_for_html_plot(self):
        fig = create_seaborn_fig_from_data_and_definition(
            self.data, self.graphic_dict[PLOT_SPECIFIC_INFO]
        )
        seaborn_fig_bytes = get_canvas_for_rendering_in_html(fig)
        fig_size = self.graphic_dict[PLOT_SPECIFIC_INFO][LAYOUT][FIGSIZE]
        # ASPECT_RATIO makes sure that the image on the webpage has the same aspect ratio as the seaborn figure
        self.graph_json_str = json.dumps(
            {
                SEABORN_PLOT_BYTES: seaborn_fig_bytes,
                ASPECT_RATIO: fig_size[0] / fig_size[1],
            }
        )

    @staticmethod
    def get_graph_html_template() -> str:
        return "seaborn.html"

    def get_data_columns(self) -> set:
        """
        extracts what columns of data are needed from the plot_options
        :param plot_options:
        :return:
        """
        plot_options = self.graphic_dict[PLOT_SPECIFIC_INFO]
        set_of_column_names = set()
        for dict_of_data_for_each_plot in plot_options[DATA]:
            for axis in POSSIBLE_AXIS:
                if axis in dict_of_data_for_each_plot:
                    set_of_column_names.add(dict_of_data_for_each_plot[axis])
            for error_axis in POSSIBLE_ERROR_AXES:
                if error_axis in dict_of_data_for_each_plot:
                    # this is error specified in data
                    set_of_column_names.add(
                        dict_of_data_for_each_plot[error_axis][ARRAY_STRING]
                    )

            for plot_attribute in PLOT_DATA_DEFINED_ATTRIBUTES:
                # column names are a string. Check for this to make sure that
                # the attribute in plot_data_defined_attributes is defined using a data
                # key and not a vector of values
                if isinstance(dict_of_data_for_each_plot.get(plot_attribute), str):
                    set_of_column_names.add(dict_of_data_for_each_plot[plot_attribute])

        return set_of_column_names
