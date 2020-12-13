import copy

from utility.build_plotly_schema import build_plotly_schema_individual_dicts
from utility.build_schema import *
from utility.constants import PROPERTIES, REQUIRED, ENUM


def build_main_schemas_for_ui():
    schema_database = build_settings_schema()
    schema_database[PROPERTIES][DATA_BACKEND][ENUM] = POSTGRES
    return {POSTGRES: schema_database}


def build_graphic_schemas_for_ui(
    data_source_names=None,
    column_names=None,
    filter_column_names=None,
    numerical_filter_column_names=None,
    unique_entries=None,
    collapse_dict=None,
):
    """
    Builds 4 separate schemas to be used by the UI
    :param data_source_names:
    :param column_names:
    :return:
    """
    graphic_schema = build_graphic_schema(
        data_source_names,
        column_names,
        filter_column_names,
        numerical_filter_column_names,
        unique_entries,
        collapse_dict,
    )
    # update these dictionaries when we add other plotting libraries
    plotly_schemas, schema_to_type = build_plotly_schema_individual_dicts(column_names)
    visualization_schema = graphic_schema[PROPERTIES].pop(VISUALIZATION_OPTIONS)
    selector_schema = graphic_schema[PROPERTIES].pop(SELECTABLE_DATA_DICT)
    graphic_schema[REQUIRED].remove(PLOT_SPECIFIC_INFO)
    del graphic_schema[PROPERTIES][PLOT_SPECIFIC_INFO]
    graphic_schemas = {
        GRAPHIC_SCHEMA: graphic_schema,
        PLOTLY_SCHEMA: plotly_schemas,
        VISUALIZATION_SCHEMA: visualization_schema,
        SELECTOR_SCHEMA: selector_schema,
    }
    return graphic_schemas, schema_to_type
