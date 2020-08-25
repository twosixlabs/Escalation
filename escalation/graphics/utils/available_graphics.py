# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

from graphics.plotly_plot import PlotlyPlot
from graphics.bootstrap_table import BootstrapTable

"""
List of the available graphics
"""

AVAILABLE_GRAPHICS = {
    "plotly": {"object": PlotlyPlot, "graph_html_template": "plotly.html"},
    "bootstrap-table": {
        "object": BootstrapTable,
        "graph_html_template": "bootstrap-table.html",
    },
}
