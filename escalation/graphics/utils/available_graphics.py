# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
from graphics.build_cytoscape_schema import CytoscapeGraphicSchema
from graphics.build_plotly_schema import PlotlyGraphicSchema
from graphics.build_seaborn_schema import SeabornGraphicSchema
from graphics.cytoscape import Cytoscape
from graphics.plotly_plot import PlotlyPlot
from graphics.seaborn_plot import SeabornPlot
from graphics.bootstrap_table import BootstrapTable
from utility.constants import (
    GRAPH_HTML_TEMPLATE,
    OBJECT,
    SCHEMA_CLASS,
)

"""
List of the available graphics
"""

AVAILABLE_GRAPHICS = {
    "plotly": {OBJECT: PlotlyPlot, SCHEMA_CLASS: PlotlyGraphicSchema,},
    "cytoscape": {OBJECT: Cytoscape, SCHEMA_CLASS: CytoscapeGraphicSchema,},
    # "bootstrap-table": {
    #    "object": BootstrapTable,
    #    GRAPH_HTML_TEMPLATE: "bootstrap-table.html",
    # },
    "seaborn": {OBJECT: SeabornPlot, SCHEMA_CLASS: SeabornGraphicSchema,},
}

PLOT_DELIMITER = ";"


# VALUE is what our backend expects - DO NOT use PLOT_DELIMITER in VALUE
# GRAPHIC_NAME is the option shown to the user


def get_all_available_graphics():
    all_graphics_dict = {}
    for plot_manager, plot_dict in AVAILABLE_GRAPHICS.items():
        all_graphics_dict[plot_manager] = plot_dict[SCHEMA_CLASS].get_available_plots()
    return all_graphics_dict
