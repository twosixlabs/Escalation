# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

# selectors are dropdowns, checkboxes etc.
from utility.constants import SELECT_HTML_TEMPLATE, SELECTOR_TYPE, TEXT, SELECTOR_NAME

AVAILABLE_SELECTORS = {
    "filter": {
        SELECT_HTML_TEMPLATE: "selector.html",
        TEXT: "Filter by {}",
        SELECTOR_NAME: "filter_{}",
    },
    "axis": {
        SELECT_HTML_TEMPLATE: "selector.html",
        TEXT: "{} axis",
        SELECTOR_NAME: "axis_{}",
    },
    "groupby": {
        SELECT_HTML_TEMPLATE: "selector.html",
        TEXT: "Group by:",
        SELECTOR_NAME: "groupby",
    },
    "numerical_filter": {
        SELECT_HTML_TEMPLATE: "numerical_filter.html",
        TEXT: "Filter by {}",
        SELECTOR_NAME: "numerical_filter_{}",
    },
}
