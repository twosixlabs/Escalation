# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

from collections import OrderedDict
from operator import eq, gt, ge, le, lt

from utility.constants import (
    SELECTOR_TYPE,
    FILTER,
    SELECTED,
    NUMERICAL_FILTER,
    OPERATION,
    VALUE,
)


OPERATIONS_FOR_NUMERICAL_FILTERS = OrderedDict(
    [(">", gt), (">=", ge), ("=", eq), ("<=", le), ("<", lt)]
)


def local_csv_handler_filter_operation(data_column, filter_dict):
    """
    Applies filter operations for queries in the LocalCsvHandler
    :param data_column: Pandas column reference
    :param filter_dict:
    :return: an operation function that can be applied on the pandas dataframe
    """
    if filter_dict[SELECTOR_TYPE] == FILTER:
        entry_values_to_be_shown_in_plot = filter_dict[SELECTED]  # Always a list
        return data_column.isin(entry_values_to_be_shown_in_plot)

    elif filter_dict[SELECTOR_TYPE] == NUMERICAL_FILTER:
        operation_function = OPERATIONS_FOR_NUMERICAL_FILTERS[filter_dict[OPERATION]]
        return operation_function(data_column, filter_dict[VALUE])


def sql_handler_filter_operation(data_column, filter_dict):
    """
    Applies filter operations for queries in the SqlHandler.
    Identical to local_csv_handler_filter_operation except for the `in_` operator for matching multiple values
    :param data_column: sql column object
    :param filter_dict:
    :return: an operation function that can be applied on the query when executed
    """
    if filter_dict[SELECTOR_TYPE] == FILTER:
        entry_values_to_be_shown_in_plot = filter_dict[SELECTED]  # Always a list
        # data backends may handle a single value differently from multiple values for performance reasons
        if len(entry_values_to_be_shown_in_plot) > 1:
            return data_column.in_(entry_values_to_be_shown_in_plot)
        else:
            return eq(data_column, entry_values_to_be_shown_in_plot[0])
    elif filter_dict[SELECTOR_TYPE] == NUMERICAL_FILTER:
        operation_function = OPERATIONS_FOR_NUMERICAL_FILTERS[filter_dict[OPERATION]]
        return operation_function(data_column, filter_dict[VALUE])
