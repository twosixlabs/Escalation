# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
from graphics.bootstrap_schema import BootstrapTableSchema
from graphics.cytoscape_schema import CytoscapeGraphicSchema
from graphics.plotly_schema import PlotlyGraphicSchema
from graphics.seaborn_schema import SeabornGraphicSchema
from graphics.cytoscape_plot import Cytoscape
from graphics.plotly_plot import PlotlyPlot
from graphics.seaborn_plot import SeabornPlot
from graphics.bootstrap_table import BootstrapTable
from utility.constants import GRAPHICS_CLASS, SCHEMA_CLASS, PREVIEW_SUPPORT

"""
List of the available graphics
see plotly for an example
"""

AVAILABLE_GRAPHICS = {
    "plotly": {
        GRAPHICS_CLASS: PlotlyPlot,  # implements instance of the Graphic class (see graphic_plot.py) for plotly
        SCHEMA_CLASS: PlotlyGraphicSchema,  # implements instance of the GraphicsConfigInterfaceBuilder
        # class (see graphic_schema.py) for plotly
        PREVIEW_SUPPORT: True,  # whether preview functionality is supported in the wizard
    },
    "cytoscape": {
        GRAPHICS_CLASS: Cytoscape,
        SCHEMA_CLASS: CytoscapeGraphicSchema,
        PREVIEW_SUPPORT: True,
    },
    "seaborn": {
        GRAPHICS_CLASS: SeabornPlot,
        SCHEMA_CLASS: SeabornGraphicSchema,
        PREVIEW_SUPPORT: True,
    },
    "bootstrap-table": {
        GRAPHICS_CLASS: BootstrapTable,
        SCHEMA_CLASS: BootstrapTableSchema,
        PREVIEW_SUPPORT: False,
    },
}

PLOT_DELIMITER = ";"


# VALUE is what our backend expects - DO NOT use PLOT_DELIMITER in VALUE
# GRAPHIC_NAME is the option shown to the user


def get_all_available_graphics():
    all_graphics_dict = {}
    for plot_manager, plot_dict in AVAILABLE_GRAPHICS.items():
        all_graphics_dict[plot_manager] = plot_dict[SCHEMA_CLASS].get_available_plots()
    return all_graphics_dict
