import copy

from utility.build_plotly_schema import build_plotly_schema_individual_dicts
from utility.build_schema import *
from utility.constants import PROPERTIES, REQUIRED, ENUM


def build_main_schemas_for_ui():
    schema_local = build_settings_schema()
    schema_database = copy.deepcopy(schema_local)
    schema_local[PROPERTIES][DATA_BACKEND][ENUM] = LOCAL_CSV
    schema_database[PROPERTIES][DATA_BACKEND][ENUM] = POSTGRES
    return {LOCAL_CSV: schema_local, POSTGRES: schema_database}


def build_graphic_schemas_for_ui(
    data_source_names=None, column_names=None, unique_entries=None, collapse_dict=None
):
    """
    If you are using the app with plotly this puts the plotly schema into the graphic schema
    :param data_source_names:
    :param column_names:
    :return:
    """
    graphic_schema = build_graphic_schema(
        data_source_names, column_names, unique_entries, collapse_dict
    )
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
