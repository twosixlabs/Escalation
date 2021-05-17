# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import json
import plotly
from flask import render_template
from graphics.graphic_class import Graphic, get_key_for_form, make_filter_dict
from utility.constants import (
    GROUPBY,
    SCATTER,
    SCATTERGL,
    TYPE,
    DATA,
    LAYOUT,
    ARRAY_STRING,
    TRANSFORMS,
    GROUPS,
    HOVERTEXT,
    AGGREGATE,
    NO_GROUP_BY,
    ACTIVE_SELECTORS,
    DEFAULT_SELECTED,
    PLOT_SPECIFIC_INFO,
    X,
    Y,
    Z,
    ERROR_X,
    ERROR_Y,
    ERROR_Z,
    SELECTABLE_DATA_DICT,
    ENTRIES,
)

HOVER_TEMPLATE_HTML = "hover_template.html"

PLOT_AXIS = "{}axis"
TITLE = "title"
CUSTOM_DATA = "customdata"
HOVER_TEMPLATE = "hovertemplate"
VISUALIZATION_TYPE = "type"
PLOTLY_TYPE = "type"
OPTIONS = "options"
STYLES = "styles"
PLOT_OPTIONS = "plot_options"
NA_FILL_IN = "NA"
TABLE = "table"
CELLS = "cells"
HEADER = "header"
VALUES = "values"
MODE = "mode"
LINES = "lines"
AXIS_TO_SORT_ALONG = "x"
AUTOMARGIN = "automargin"
HOVERMODE = "hovermode"
CLOSEST = "closest"
POSSIBLE_AXIS = [X, Y, Z]
POSSIBLE_ERROR_AXES = [ERROR_X, ERROR_Y, ERROR_Z]

CONFIG = "config"

MODE_BAR_REMOVE = "modeBarButtonsToRemove"
MODE_BAR_ADD = "modeBarButtonsToAdd"

DISPLAY_LOGO = "displaylogo"
UPDATE_MENUS = "updatemenus"
BUTTONS = "buttons"


def does_data_need_to_be_sorted(plot_info_data_dict: dict):
    """
    Determines whether the data needs to be sorted if so does it inplace
    :param data_dict:
    :return:
    """
    # conditions when data needs to be sorted
    if plot_info_data_dict[PLOTLY_TYPE] in [SCATTER, SCATTERGL] and (
        MODE not in plot_info_data_dict or LINES in plot_info_data_dict[MODE]
    ):
        return True
    return False


def add_layout_axis_defaults(layout_dict: dict, axis, column_name):
    """
    Adds defaults to the layout to the plotly graph for a better viewing experience
    :param layout_dict:
    :param axis:
    :param column_name:
    :return:
    """
    if PLOT_AXIS.format(axis) not in layout_dict:
        layout_dict[PLOT_AXIS.format(axis)] = {TITLE: column_name}
    if AUTOMARGIN not in layout_dict[PLOT_AXIS.format(axis)]:
        layout_dict[PLOT_AXIS.format(axis)][AUTOMARGIN] = True
    return layout_dict


def add_config_defaults(config_dict: dict):
    """
    Removes buttons from the mode bar
    :param config_dict:
    :return:
    """
    if MODE_BAR_REMOVE not in config_dict:
        config_dict[MODE_BAR_REMOVE] = [
            "select2d",
            "lasso2d",
            "autoScale2d",
            "toggleSpikelines",
        ]
    if DISPLAY_LOGO not in config_dict:
        config_dict[DISPLAY_LOGO] = False
    return config_dict


def add_toggle_layout_button(layout_dict: dict):
    """
    Adds a button that toggles the legend
    :param layout_dict:
    :return:
    """
    updatemenus = layout_dict.get(UPDATE_MENUS, [])
    updatemenus.append(
        {
            TYPE: BUTTONS,
            BUTTONS: [
                {
                    "method": "relayout",
                    "label": "Show/Hide Legend",
                    "args": ["showlegend", True],
                    "args2": ["showlegend", False],
                }
            ],
            # these align the button with the legend labels
            "xanchor": "left",
            "yanchor": "bottom",
            X: 1.0,
            Y: 1.0,
            "pad": {"r": 2, "l": 38},
        }
    )
    layout_dict[UPDATE_MENUS] = updatemenus
    return layout_dict


class PlotlyPlot(Graphic):
    def make_dict_for_html_plot(self):
        """
        Makes the json file that plotly takes in
        :param data: a pandas dataframe
        :param plot_options:
        :param visualization_options:
        :return:
        """
        plot_options = self.graphic_dict[PLOT_SPECIFIC_INFO]
        # todo: cut off all text data to used in group by or titles to 47 charaters
        data_sorted = False
        plot_options[CONFIG] = add_config_defaults(plot_options.get(CONFIG, {}))
        # only have a legend if there is more than one plot by having a group by.
        # Future: if we support having more than graphic plotted need-
        # or len(plot_options[DATA]) > 1 with some other logic.

        for index, plotly_data_dict in enumerate(plot_options[DATA]):
            if GROUPBY in plotly_data_dict.get(TRANSFORMS, {}):
                plot_options[LAYOUT] = add_toggle_layout_button(
                    plot_options.get(LAYOUT, {})
                )
            if not data_sorted and does_data_need_to_be_sorted(plotly_data_dict):
                self.data.sort_values(
                    plotly_data_dict[AXIS_TO_SORT_ALONG], inplace=True
                )
                data_sorted = True
            for axis in POSSIBLE_AXIS:
                if axis in plotly_data_dict:

                    if index == 0:
                        # if there is no label, label the columns with the first lines/scatters column names
                        layout_dict = plot_options.get(LAYOUT, {})
                        if HOVERMODE not in layout_dict:
                            layout_dict[HOVERMODE] = CLOSEST
                        plot_options[LAYOUT] = add_layout_axis_defaults(
                            layout_dict, axis, plotly_data_dict[axis]
                        )
                    # moving the contents of the data to where plotly expects it
                    # from the output of the database
                    plotly_data_dict[axis] = self.data[plotly_data_dict[axis]]
            for error_axis in POSSIBLE_ERROR_AXES:
                if error_axis in plotly_data_dict:
                    plotly_data_dict[error_axis][ARRAY_STRING] = self.data[
                        plotly_data_dict[error_axis][ARRAY_STRING]
                    ]
            if TRANSFORMS in plotly_data_dict:
                plotly_data_dict[TRANSFORMS] = self.put_data_in_transforms(
                    plotly_data_dict[TRANSFORMS]
                )
            if HOVERTEXT in plotly_data_dict:
                plotly_data_dict = self.get_hover_data_in_plotly_form(plotly_data_dict)

        self.graph_json_str = json.dumps(
            plot_options, cls=plotly.utils.PlotlyJSONEncoder
        )

    def get_hover_data_in_plotly_form(self, plotly_data_dict):
        hover_column_names = plotly_data_dict.pop(HOVERTEXT, [])
        # transposes a list of lists of column data to a list of lists of row data
        plotly_data_dict[CUSTOM_DATA] = list(
            map(list, zip(*[self.data[col_name] for col_name in hover_column_names]),)
        )

        plotly_data_dict[HOVER_TEMPLATE] = render_template(
            HOVER_TEMPLATE_HTML, hover_column_names=hover_column_names
        )
        return plotly_data_dict

    def put_data_in_transforms(self, transform_dict):
        """
        puts the data into the transform dictionary in the form 1st elem, 2 elem, ...
        :param transform_list:
        :return:
        """

        def concatenate_columns(transform_dict):
            transform_dict[GROUPS] = [
                ", ".join(map(str, data_list))
                for data_list in zip(
                    *[self.data[col_name] for col_name in transform_dict[GROUPS]]
                )
            ]
            return transform_dict

        transform_list = []
        for transform_type, transform in transform_dict.items():
            if transform_type == GROUPBY:
                transform = concatenate_columns(transform)
                transform[TYPE] = GROUPBY
                transform_list.append(transform)
            elif transform_type == AGGREGATE:
                for aggregate_dict in transform:
                    aggregate_dict = concatenate_columns(aggregate_dict)
                    aggregate_dict[TYPE] = AGGREGATE
                    transform_list.append(aggregate_dict)

        return transform_list

    @staticmethod
    def get_graph_html_template() -> str:
        return "plotly.html"

    def get_data_columns(self) -> set:
        """
        extracts what columns of data are needed from the self.graphic_dict[PLOT_SPECIFIC_INFO]
        :param plot_options:
        :return:
        """
        plot_options = self.graphic_dict[PLOT_SPECIFIC_INFO]
        set_of_column_names = set()
        for data_dict_per_plot in plot_options[DATA]:
            for axis in POSSIBLE_AXIS:
                if axis in data_dict_per_plot:
                    set_of_column_names.add(data_dict_per_plot[axis])
            for error_axis in POSSIBLE_ERROR_AXES:
                if error_axis in data_dict_per_plot:
                    # this is error specified in data
                    set_of_column_names.add(
                        data_dict_per_plot[error_axis][ARRAY_STRING]
                    )

            for transform_type, transform in data_dict_per_plot.get(
                TRANSFORMS, {}
            ).items():
                if transform_type == GROUPBY:
                    set_of_column_names.update(
                        [column_name for column_name in transform.get(GROUPS, [])]
                    )
                elif transform_type == AGGREGATE:
                    for transform_dict in transform:
                        set_of_column_names.update(
                            [
                                column_name
                                for column_name in transform_dict.get(GROUPS, [])
                            ]
                        )

            set_of_column_names.update(
                [column_name for column_name in data_dict_per_plot.get(HOVERTEXT, [])]
            )

        return set_of_column_names

    def add_active_selectors_to_selectable_data_list(self):

        super().add_active_selectors_to_selectable_data_list()

        selectable_data_dict = self.graphic_dict[SELECTABLE_DATA_DICT]
        if GROUPBY in selectable_data_dict:
            group_by_dict = selectable_data_dict[GROUPBY]
            selected_group_by = self.addendum_dict.get(
                get_key_for_form(GROUPBY, ""), []
            )
            if NO_GROUP_BY in selected_group_by:
                group_by_dict[ACTIVE_SELECTORS] = [NO_GROUP_BY]
            else:
                group_by_dict[ACTIVE_SELECTORS] = (
                    selected_group_by
                    or group_by_dict.get(DEFAULT_SELECTED, [NO_GROUP_BY])
                )

    def modify_graphic_dict_based_on_addendum_dict(self):
        selectable_data_dict = self.graphic_dict[SELECTABLE_DATA_DICT]
        if GROUPBY in selectable_data_dict:
            selection = self.addendum_dict.get(
                get_key_for_form(GROUPBY, "")
            ) or selectable_data_dict[GROUPBY].get(DEFAULT_SELECTED, [NO_GROUP_BY])
            if NO_GROUP_BY not in selection:
                # put selection in groups in the groupby dict without changing anythong else
                transform_dict = self.graphic_dict[PLOT_SPECIFIC_INFO][DATA][0].get(
                    TRANSFORMS, {}
                )
                groupby_dict = transform_dict.get(GROUPBY, {})
                groupby_dict[GROUPS] = selection
                transform_dict[GROUPBY] = groupby_dict
                self.graphic_dict[PLOT_SPECIFIC_INFO][DATA][0][
                    TRANSFORMS
                ] = transform_dict

    def create_data_subselect_info_for_plot(self):

        selectable_data_dict = self.graphic_dict.get(SELECTABLE_DATA_DICT, {})
        if GROUPBY in selectable_data_dict:
            group_by_dict = selectable_data_dict[GROUPBY]
            selector_entries = group_by_dict[ENTRIES]
            selector_entries.sort()
            # append no_group_by to the front of the list
            selector_entries.insert(0, NO_GROUP_BY)
            self.select_info.append(
                make_filter_dict(GROUPBY, group_by_dict, "", selector_entries)
            )

        super().create_data_subselect_info_for_plot()
