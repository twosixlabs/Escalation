# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import copy

from graphics.plotly_plot import (
    PlotlyPlot,
    LAYOUT,
    TITLE,
    PLOT_AXIS,
    VISUALIZATION_TYPE,
    AGGREGATIONS,
    OPTIONS,
    AGGREGATE,
    TRANSFORMS,
)
import pytest
import json
import pandas as pd

from utility.constants import POINTS_NUM, DATA, OPTION_COL

TITLE1 = "random_num"
TITLE2 = "another_rand"


@pytest.fixture()
def make_data():
    data = {
        TITLE1: [3, 6, 7],
        TITLE2: [4, 8, 1],
    }

    return pd.DataFrame(data)


def test_plotly_draw_scatter(make_data):
    plot_options = {
        DATA: [{"type": "scatter", "x": TITLE1, "y": TITLE2, "mode": "markers"}]
    }

    ploty_test = PlotlyPlot()
    graph_json = ploty_test.make_dict_for_html_plot(make_data, plot_options)
    graph_dict = json.loads(graph_json)

    assert (graph_dict[DATA][0]["x"] == make_data[TITLE1]).all()
    assert (graph_dict[DATA][0]["y"] == make_data[TITLE2]).all()
    assert graph_dict[LAYOUT][PLOT_AXIS.format("x")][TITLE] == TITLE1
    assert graph_dict[LAYOUT][PLOT_AXIS.format("y")][TITLE] == TITLE2
    # assert graph_dict[LAYOUT][PLOT_AXIS.format("x")][AUTOMARGIN]
    # assert graph_dict[LAYOUT][PLOT_AXIS.format("y")][AUTOMARGIN]
    assert len(graph_dict[DATA][0][TRANSFORMS]) == 0


def test_plotly_visualization_options(make_data, test_app_client):
    plot_options = {
        DATA: [{"type": "scatter", "x": TITLE1, "y": TITLE2, "mode": "markers"}]
    }
    ploty_test = PlotlyPlot()
    visualization_options = {
        "hover_data": {OPTION_COL: [TITLE1],},  # need a flask app to run
        AGGREGATE: {OPTION_COL: [TITLE2], AGGREGATIONS: {"x": "avg", "y": "avg"},},
    }

    graph_json = ploty_test.make_dict_for_html_plot(
        make_data, plot_options, visualization_options
    )
    graph_dict = json.loads(graph_json)
    transform_dict = graph_dict[DATA][0][TRANSFORMS]
    assert len(transform_dict) == 1

    assert transform_dict[0][VISUALIZATION_TYPE] == AGGREGATE
    assert transform_dict[0][AGGREGATIONS][0]["target"] == "x"
    assert transform_dict[0][AGGREGATIONS][0]["func"] == "avg"
    assert transform_dict[0][AGGREGATIONS][1]["target"] == "y"
    assert transform_dict[0][AGGREGATIONS][1]["func"] == "avg"
