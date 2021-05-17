# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import copy

from graphics.plotly_plot import (
    PlotlyPlot,
    LAYOUT,
    TITLE,
    PLOT_AXIS,
    VISUALIZATION_TYPE,
    TRANSFORMS,
)
import pytest
import json
import pandas as pd

from utility.constants import (
    DATA,
    OPTION_COL,
    AGGREGATIONS,
    AGGREGATE,
    HOVERTEXT,
    TYPE,
    GROUPS,
    TARGET,
    PLOT_SPECIFIC_INFO,
)

TITLE1 = "random_num"
TITLE2 = "another_rand"


@pytest.fixture(scope="module")
def make_data():
    data = {
        TITLE1: [3, 6, 7],
        TITLE2: [4, 8, 1],
    }

    return pd.DataFrame(data)


def test_plotly_draw_scatter(make_data):
    graphic_dict = {
        PLOT_SPECIFIC_INFO: {
            DATA: [{"type": "scatter", "x": TITLE1, "y": TITLE2, "mode": "markers"}]
        }
    }

    ploty_test = PlotlyPlot(graphic_dict)
    ploty_test.data = make_data
    ploty_test.make_dict_for_html_plot()
    graph_dict = json.loads(ploty_test.graph_json_str)

    assert (graph_dict[DATA][0]["x"] == make_data[TITLE1]).all()
    assert (graph_dict[DATA][0]["y"] == make_data[TITLE2]).all()
    assert graph_dict[LAYOUT][PLOT_AXIS.format("x")][TITLE] == TITLE1
    assert graph_dict[LAYOUT][PLOT_AXIS.format("y")][TITLE] == TITLE2
    # assert graph_dict[LAYOUT][PLOT_AXIS.format("x")][AUTOMARGIN]
    # assert graph_dict[LAYOUT][PLOT_AXIS.format("y")][AUTOMARGIN]
    assert TRANSFORMS not in graph_dict[DATA][0]


def test_plotly_visualization_options(make_data, test_app_client_sql_backed):
    graphic_dict = {
        PLOT_SPECIFIC_INFO: {
            DATA: [
                {
                    "type": "scatter",
                    "x": TITLE1,
                    "y": TITLE2,
                    "mode": "markers",
                    HOVERTEXT: [TITLE1],
                    TRANSFORMS: {
                        AGGREGATE: [
                            {
                                GROUPS: [TITLE2],
                                AGGREGATIONS: [
                                    {TARGET: "x", "func": "avg"},
                                    {TARGET: "y", "func": "avg"},
                                ],
                            }
                        ]
                    },
                }
            ]
        }
    }
    ploty_test = PlotlyPlot(graphic_dict)
    ploty_test.data = make_data
    ploty_test.make_dict_for_html_plot()
    graph_dict = json.loads(ploty_test.graph_json_str)
    transform_dict = graph_dict[DATA][0][TRANSFORMS]
    assert len(transform_dict) == 1

    assert transform_dict[0][VISUALIZATION_TYPE] == AGGREGATE
    assert transform_dict[0][AGGREGATIONS][0]["target"] == "x"
    assert transform_dict[0][AGGREGATIONS][0]["func"] == "avg"
    assert transform_dict[0][AGGREGATIONS][1]["target"] == "y"
    assert transform_dict[0][AGGREGATIONS][1]["func"] == "avg"
