# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

APP_CONFIG_JSON = "app_config_json"
AVAILABLE_PAGES_DICT = "available_pages_dict"
CONFIG_FILE_FOLDER = "config_file_folder"
MAIN_CONFIG = "main_config.json"
# app config keys
AVAILABLE_PAGES = "available_pages"
GRAPHICS = "graphics"
GRAPHIC_NUM = "graphic_{:d}"
POINTS_NUM = "points_{:d}"
SITE_TITLE = "title"
SITE_DESC = "brief_desc"
WEBPAGE_LABEL = "webpage_label"
LINK = "link"
GRAPHIC_TITLE = "title"
GRAPHIC_DESC = "brief_desc"
DATA_BACKEND = "data_backend"
POSTGRES = "psql"
LOCAL_CSV = "local_csv"
PLOT_ID = "plot_id"
GRAPHIC_CONFIG_FILES = "graphic_config_files"
URL_ENDPOINT = "url_endpoint"
APP_DEPLOY_DATA = "app_deploy_data"
TEST_APP_DEPLOY_DATA = "test_app_deploy_data"
MAIN_DATA_SOURCE = "main_data_source"
ADDITIONAL_DATA_SOURCES = "additional_data_sources"
SQLALCHEMY_DATABASE_URI = "SQLALCHEMY_DATABASE_URI"
DEVELOPMENT = "development"

# Plotly constants
LAYOUT = "layout"
HEIGHT = "height"
AGGREGATE = "aggregate"
HOVER_DATA = "hover_data"
AGGREGATIONS = "aggregations"


# path to the file folder for LocalHandler or table name for SqlHandler
DATA_FILE_DIRECTORY = "data_file_directory"
DATA_SOURCES = "data_sources"
DATA_UPLOAD_METADATA = "data_upload_metadata"
NEW_DATA_SOURCE = "new_data_source"
DATA_SOURCE_TYPE = "data_source_type"
JOIN_KEYS = "join_keys"
DATA_LOCATION = "filepath"
TABLE_COLUMN_SEPARATOR = ":"
DEFAULT_SELECTED = "default_selected"
CURRENT_PAGE = "current_page"
DATA = "data"
DATA_FILTERS = "data_filters"
PLOT_MANAGER = "plot_manager"
VISUALIZATION_OPTIONS = "visualization_options"
DATA_TO_PLOT_PATH = "data_to_plot_path"
PLOT_SPECIFIC_INFO = "plot_specific_info"
FILTERS = "filters"
DATABASE = "database"
SELECTABLE_DATA_DICT = "selectable_data_dict"
OPTION_TYPE = "type"
OPTION_COL = "column"

PAGE_NAME = "name"

# Available graphics keys
GRAPH_HTML_TEMPLATE = "graph_html_template"
OBJECT = "object"

# Available selector keys
SELECT_HTML_TEMPLATE = "select_html_template"
COLUMN_NAME = "column"
ENTRIES = "entries"
TEXT = "text"
SELECT_OPTION = "options"
AXIS = "axis"
GROUPBY = "groupby"
SELECTOR_TYPE = "type"
FILTER = "filter"
UNFILTERED_SELECTOR = "unfiltered_selector"
NUMERICAL_FILTER = "numerical_filter"
INEQUALITIES = "inequalities"
OPERATION = "operation"
VALUE = "value"
SELECTED = "selected"
INEQUALITY_LOC = "inequality_{}"
UPPER_INEQUALITY = "upper"
LOWER_INEQUALITY = "lower"
LIST_OF_VALUES = "list_of_values"
MULTIPLE = "multiple"
NO_GROUP_BY = "No Group By"
SELECTOR_NAME = "name"

# ALL of row
SHOW_ALL_ROW = "Show All Rows"

# JINJA CONSTANTS
JINJA_PLOT = "plots"
JINJA_BUTTONS = "buttons"
JINJA_GRAPH_HTML_FILE = "graph_html_file"
JINJA_SELECT_HTML_FILE = "select_html_file"
JINJA_SELECT_INFO = "select_info"
JINJA_PLOT_INFO = "plot_info"
ACTIVE_SELECTORS = "active_selector"


# DATA MANAGEMENT
INDEX_COLUMN = "row_index"
UPLOAD_ID = "upload_id"
UPLOAD_TIME = "upload_time"
USERNAME = "username"
NOTES = "notes"
INACTIVE = "inactive"
ACTIVE = "active"
TABLE_NAME = "table_name"
DATA_SOURCE = "data_source"
CSVFILE = "csvfile"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# addendum constants
GRAPHIC_NAME = "graphic_name"
NUMERICAL_FILTER_NUM_LOC_TYPE = "numerical_filter_{:d}_{}_{}"
PROCESS = "process"

# setup constants
PAGE_ID = "page_id"
GRAPHIC = "graphic"
CONFIG_DICT = "config_dict"
GRAPHIC_STATUS = "graphic_status"
COPY = "copy"
OLD = "old"
NEW = "new"

# schema constants, these come from json schema
ADDITIONAL_PROPERTIES = "additionalProperties"
PROPERTIES = "properties"
PATTERN_PROPERTIES = "patternProperties"
DESCRIPTION = "description"
TITLE = "title"
TYPE = "type"
ITEMS = "items"
PATTERN = "pattern"
REQUIRED = "required"
MIN_ITEMS = "minItems"
OPTIONS = "options"
DEPENDENCIES = "dependencies"
ENUM = "enum"
ONEOF = "oneOf"

# schema constants, these come from https://github.com/json-editor/json-editor
HIDDEN = "hidden"
DISABLE_COLLAPSE = "disable_collapse"
COLLAPSED = "collapsed"
DISABLE_PROPERTIES = "disable_properties"
REMOVE_EMPTY_PROPERTIES = "remove_empty_properties"

# plotly constants

SCATTER = "scatter"
SCATTERGL = "scattergl"

# schema constants
GRAPHIC_SCHEMA = "graphic_schema"
PLOTLY_SCHEMA = "plotly_schema"
VISUALIZATION_SCHEMA = "visualization_schema"
SELECTOR_SCHEMA = "selector_schema"

VISUALIZATION = "visualization"
SELECTOR = "selector"
PLOTLY = "plotly"
GRAPHIC_META_INFO = "graphic_meta_info"
GRAPHIC_PATH = "graphic_path"
