# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import copy
from collections import defaultdict
from itertools import product

from elasticsearch_dsl import Search
from database.data_handler import DataHandler
from flask import current_app

from utility.available_selectors import (
    AVAILABLE_SELECTORS,
    get_key_for_form,
    make_filter_dict,
    convert_string_for_numerical_filter,
)

from utility.constants import *

DEFAULT_SIZE = 50


def get_keys_and_types(mapper_dict: dict):
    """
    Goes through a dictionary returned by the get_mapper function of elasticsearch and finds the keys.
    :param mapper_dict:
    :return:
    """
    key_type_dict = {}
    for key, value in mapper_dict.items():
        if PROPERTIES in value:
            key_type_dict.update(
                {
                    ".".join([key, deeper_key]): key_dict
                    for deeper_key, key_dict in get_keys_and_types(
                        value[PROPERTIES]
                    ).items()
                }
            )
        else:
            key_type = value[TYPE]
            key_type_dict[key] = {TYPE: key_type}
            if key_type == TEXT:
                key_type_dict[key][FIELD_DATA] = value.get(FIELD_DATA, False)

        if FIELDS in value:
            key_type_dict.update(
                {
                    ".".join([key, deeper_key]): key_dict
                    for deeper_key, key_dict in get_keys_and_types(
                        value[FIELDS]
                    ).items()
                }
            )
    return key_type_dict


def add_sort_to_search(search: Search, sort_list: list):
    sort_list_es = []
    for sort_dict in sort_list:
        field_name = sort_dict.pop(FIELD)
        if sort_dict:
            sort_list_es.append({field_name: sort_dict})
        else:
            sort_list_es.append(field_name)
    # sort takes in the name of the field or dictionaries as arguments
    # So we form a list and expand it
    search = search.sort(*sort_list_es)
    return search


def add_term_to_search(search: Search, term_list: list):
    for term_dict in term_list:
        field = term_dict[FIELD]
        entries = term_dict[ENTRIES]
        # filter takes in the name of the field as an argument
        # Since we do not know the filed name a priori we have to evaluate it in the dict and expand it
        if len(entries) == 1:
            search = search.filter("term", **{field: entries[0]})
        else:
            search = search.filter("terms", **{field: entries})
    return search


def add_range_to_search(search: Search, range_list: list):
    for range_dict in range_list:
        # filter takes in the name of the field as an argument
        # Since we do not know the filed name a priori we have to evaluate it in the dict and expand it
        search = search.filter(
            "range", **{range_dict[FIELD]: {range_dict[OPERATION]: range_dict[VALUE]}}
        )
    return search


def add_match_to_search(search: Search, match_list):
    for match_dict in match_list:
        match_dict_copy = match_dict.copy()
        fields = match_dict_copy.pop(FIELDS)
        # To cover the case where USER_SELECTABLE does not exist, we are popping instead of deleting
        match_dict_copy.pop(USER_SELECTABLE, None)
        # todo key checking?
        # https://www.elastic.co/guide/en/elasticsearch/reference/7.12/query-dsl-multi-match-query.html#query-dsl-multi-match-query
        if len(fields) == 1:
            # match takes in the name of the field as an argument
            # Since we do not know the filed name a priori we have to evaluate it in the dict and expand it
            search = search.query("match", **{fields[0]: match_dict_copy})
        else:
            match_dict[FIELDS] = fields
            search = search.query("multi_match", match_dict)
    return search


def add_aggregations_to_search(search: Search, aggregations_dict: dict):
    """
    aggregations_dict is a dictionary that contains a list of the aggregations on key buckets
    as well as the metric to perform across the buckets. See elasticsearch schema key AGGREGATIONS for more info
    :param search:
    :param aggregations_dict:
    :return:
    """
    bucket_list = aggregations_dict.get(BUCKETS, [])
    metric = aggregations_dict.get(METRIC, COUNT)
    # aggregation add to search is an in place operation
    cur_bucket = search.aggs
    # aggregations stack. cur_bucket is the current bucket the aggregation is stacking to
    # Sorting according to the metric needs to go into the last bucket. We always use the default
    # sort is metric == COUNT
    if metric != COUNT and bucket_list:
        bucket_list[-1][ORDER] = {
            aggregations_dict[METRIC_FIELD]: aggregations_dict.get(SORT_ORDER, "desc")
        }

    for index, bucket in enumerate(bucket_list):
        if bucket[AGG_TYPE] == DATE_HISTOGRAM_AGGREGATION:
            interval = bucket.pop(INTERVAL, 1)
            units = bucket.pop(UNITS, "h")  # defaults to hours (h)
            bucket[FIXED_INTERVAL] = f"{interval}{units}"
        # the FIELD key is getting used as the name and the field arguments
        cur_bucket = cur_bucket.bucket(bucket[FIELD], **bucket)

    # so metric == COUNT is always calculated by elasticsearch.
    # All other metrics need to be specified after the buckets
    if metric != COUNT:
        cur_bucket.metric(
            aggregations_dict[METRIC_FIELD],
            metric,
            field=aggregations_dict[METRIC_FIELD],
        )
    return search


def add_significant_terms_to_search(search: Search, significant_terms_dict):
    pass


def add_significant_text_to_search(search: Search, significant_text_dict):
    pass


def get_data_from_response_hits(response, cols: set, orient=LIST):
    if orient == "list":
        cols_dict = {col_name: [] for col_name in cols}
        for hit in response:
            list_of_data = [getattr(hit, col_name, [None]) for col_name in cols]
            # product is taking the cartesian product, this ensures all columns have the same number of elements
            for data_tuple in product(*list_of_data):
                for col_name, element in zip(cols, data_tuple):
                    cols_dict[col_name].append(element)
        return cols_dict
    elif orient == RECORDS:
        col_data = []
        for hit in response:
            col_data.append(hit.to_dict())
        return col_data


def extract_agg_data(agg: dict, bucket_list, bucket_ind=0, num_buckets=1):
    """
    A recursive function that pulls the data from an aggregation response
    agg: part of the response from elasticsearch
    """
    bucket = bucket_list[bucket_ind]
    field = bucket[FIELD]
    agg_type = bucket[AGG_TYPE]
    key = "key_as_string" if agg_type == DATE_HISTOGRAM_AGGREGATION else "key"

    if agg_type == METRIC:
        return {field: [agg[field][VALUE]]}, 1
    cols_dict = defaultdict(list)
    index = -1
    for index, new_agg in enumerate(agg[field]):
        if bucket_ind < num_buckets - 1:
            temp_cols_dict, count = extract_agg_data(
                new_agg, bucket_list, bucket_ind + 1, num_buckets
            )

            for col_name in temp_cols_dict:
                cols_dict[col_name].extend(temp_cols_dict[col_name])
            if temp_cols_dict:
                cols_dict[field].extend([new_agg[key]] * count)

        else:
            # This is reached if *doc_count* is chosen as the metric and we are on the last bucket
            cols_dict[field].append(new_agg[key])
            cols_dict[DOC_COUNT].append(new_agg[DOC_COUNT])

    return cols_dict, index + 1


def get_data_from_response_aggregations(
    response, cols: set, aggregations_dict, orient=LIST
):
    """
    :param response: An elasticsearch response object
    """
    bucket_list = aggregations_dict[BUCKETS]
    metric = aggregations_dict.get(METRIC, COUNT)
    bucket_fields = [bucket[FIELD] for bucket in bucket_list]
    if metric != COUNT:
        metric_field = aggregations_dict[METRIC_FIELD]
        bucket_fields.append(metric_field)
        bucket_list.append({FIELD: metric_field, AGG_TYPE: METRIC})
    else:
        bucket_fields.append(DOC_COUNT)

    if not cols.issubset(bucket_fields):
        raise ValueError("cols in plot is not subset of bucket fields")
    num_buckets = len(bucket_list)
    cols_dict = extract_agg_data(response.aggregations, bucket_list, 0, num_buckets)[0]
    if orient == RECORDS:
        # converts a dictionary of lists to a list of dictionaries
        cols_dict = [dict(zip(cols_dict, t)) for t in zip(*cols_dict.values())]

    return cols_dict


ES_KEYS_FOR_SEARCH = [
    SORT,
    FILTER_TERM,
    FILTER_RANGE,
    MATCH,
    AGGREGATIONS,
]

SEARCH_FUNCTIONS = [
    add_sort_to_search,
    add_term_to_search,
    add_range_to_search,
    add_match_to_search,
    add_aggregations_to_search,
]


def get_type(mapper_dict: dict, key: str):
    """
    Going through the mapping dictionary
    :param mapper_dict:
    :param key:
    :return:
    """
    for is_nested_key, name in enumerate(key.split(".")):
        if is_nested_key:
            mapper_dict = mapper_dict[PROPERTIES]
            mapper_dict = mapper_dict[name]
        else:
            mapper_dict = mapper_dict[name]
    return mapper_dict.get(TYPE)


REPLACE = "replace"
APPEND = "append"
FAIL = "fail"


class ElasticSearchHandler(DataHandler):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.main_data_source = self.data_sources[MAIN_DATA_SOURCE][DATA_SOURCE_TYPE]

    def get_column_data(self, cols: set, orient="list"):
        if AGGREGATIONS in self.selectable_data_dict:
            start = end = 0
        else:
            start = self.selectable_data_dict.get(FROM, 0)
            end = start + self.selectable_data_dict.get(SIZE, DEFAULT_SIZE)
        search = self.make_search_according_to_selection_dict(cols)
        # This slice is handled elastic search memory not python
        search = search[start:end]
        # This is where the query executes.
        response = search.execute()
        if AGGREGATIONS in self.selectable_data_dict:
            return get_data_from_response_aggregations(
                response, cols, self.selectable_data_dict[AGGREGATIONS], orient
            )
        else:
            return get_data_from_response_hits(response, cols, orient)

    def make_search_according_to_selection_dict(self, cols: set):
        search = Search(using=current_app.es, index=self.main_data_source)
        # This extra call ensures elasticsearch returns a list of values even if there is only one
        search = search.extra(fields=list(cols))
        search = search.source(False)
        for key, func in zip(ES_KEYS_FOR_SEARCH, SEARCH_FUNCTIONS):
            if key in self.selectable_data_dict:
                search = func(search, self.selectable_data_dict[key])
        return search

    def get_schema_for_data_source(self) -> dict:
        """
        gets the data type for each column for the current handler object
        :return: dict keyed by column name, valued with python types
        """
        mappings = "mappings"
        mapping_dict = current_app.es.indices.get_mapping(index=self.main_data_source)
        fields_dict = mapping_dict[self.main_data_source][mappings][PROPERTIES]
        col_type_dict = get_keys_and_types(fields_dict)
        return col_type_dict

    def get_column_names_for_data_source(self):
        """
        gets the column names for the current handler object
        :return: list of strings
        """
        mappings = "mappings"
        data_source = self.main_data_source
        mapping_dict = current_app.es.indices.get_mapping(index=self.main_data_source)
        column_names_and_types = get_keys_and_types(
            mapping_dict[data_source][mappings][PROPERTIES]
        )
        return list(column_names_and_types.keys()) + [DOC_COUNT]

    def get_column_unique_entries(self, cols: set) -> dict:
        """
        :param cols: list of column names
        :param filters: Optional list specifying how to filter contents of the the requested columns based on the row values
        :return: A dict keyed by column names and valued with the unique values as strings in that column
        """

        search = Search(using=current_app.es, index=self.main_data_source)
        # This extra call ensures elasticsearch returns a list of values even if there is only one
        search = search.extra(fields=list(cols))
        search = search.source(False)
        search = search.query("function_score", functions="random_score")

        cols_dict = {col_name: set() for col_name in cols}
        # We only want to output unique values in the wizard for columns with less than MAX_ENTRIES_FOR_FILTER_SELECTOR
        # entries to estimate the count we look at 2*MAX_ENTRIES_FOR_FILTER_SELECTOR entries and count the unique
        # vectors
        for hit in search[: (MAX_ENTRIES_FOR_FILTER_SELECTOR * 2)]:
            for col_name in cols:
                cols_dict[col_name].update(getattr(hit, col_name, []))

        for col_name in cols:
            set_of_entries = cols_dict[col_name]
            if len(set_of_entries) <= MAX_ENTRIES_FOR_FILTER_SELECTOR:
                cols_dict[col_name] = [str(value) for value in set_of_entries]
            else:
                del cols_dict[col_name]
        return cols_dict

    def get_column_unique_entries_based_on_type(self, cols, filter_active_data=True):
        FILTER_TYPES = ["keyword", "boolean"]
        NUMERICAL_FILTER_TYPES = [
            "long",
            "integer",
            "byte",
            "short",
            "double",
            "float",
            "half_float",
            "unsigned_long",
        ]
        schema_dict = self.get_schema_for_data_source()
        filter_dict = {FILTER: [], NUMERICAL_FILTER: [], TEXT: [], DATE: []}
        for col, col_dict in schema_dict.items():
            if col_dict[TYPE] == TEXT:
                filter_dict[TEXT].append(col)
                if col_dict.get(FIELD_DATA):
                    filter_dict[FILTER].append(col)
            elif col_dict[TYPE] == DATE:
                filter_dict[DATE].append(col)
            elif col_dict[TYPE] in FILTER_TYPES:
                filter_dict[FILTER].append(col)
            elif col_dict[TYPE] in NUMERICAL_FILTER_TYPES:
                filter_dict[NUMERICAL_FILTER].append(col)

        unique_entries_dict = self.get_column_unique_entries(set(filter_dict[FILTER]))
        return unique_entries_dict, filter_dict

    def add_instructions_to_config_dict(self):
        if self.selectable_data_dict and self.addendum_dict:
            self.add_active_selectors_to_selectable_data_dict()

    def add_active_selectors_to_selectable_data_dict(self):
        """
        Sets which selectors are active based on user choices.
        We have a selected dict (or a skeleton) that performs a query
         we update the user dict inplace with the user form
        If none have been selected sets, we set reasonable defaults
        :return:
        """
        filter_list = self.selectable_data_dict.get(FILTER_TERM, [])
        for index, filter_dict in enumerate(filter_list):
            if filter_dict.get(USER_SELECTABLE):
                selected_filters = self.addendum_dict.get(
                    get_key_for_form(FILTER, index), []
                )
                if SHOW_ALL_ROW in selected_filters:
                    filter_dict[ENTRIES] = [SHOW_ALL_ROW]
                else:
                    filter_dict[ENTRIES] = selected_filters or filter_dict.get(
                        ENTRIES, [SHOW_ALL_ROW]
                    )

        filter_range_list = self.selectable_data_dict.get(FILTER_RANGE, [])
        for index, filter_range_dict in enumerate(filter_range_list):
            if filter_range_dict.get(USER_SELECTABLE):
                user_input = self.addendum_dict.get(
                    get_key_for_form(FILTER_RANGE, index), [None]
                )[0]
                if user_input:
                    filter_range_dict[VALUE] = convert_string_for_numerical_filter(
                        user_input
                    )

        match_list = self.selectable_data_dict.get(MATCH, [])
        for index, match_dict in enumerate(match_list):
            if match_dict.get(USER_SELECTABLE):
                match_dict[QUERY] = self.addendum_dict.get(
                    get_key_for_form(MATCH, index), [match_dict.get(QUERY, "")],
                )[0]

    def create_data_subselect_info_for_plot(self):
        schema = None
        match_list = self.selectable_data_dict.get(MATCH, [])
        for index, match_dict in enumerate(match_list):
            if match_dict.get(USER_SELECTABLE):
                temp_dict = {
                    OPTION_COL: ", ".join(match_dict[FIELDS]),
                    ACTIVE_SELECTORS: match_dict.get(QUERY, ""),
                }
                self.select_info.append(make_filter_dict(MATCH, temp_dict, index))

        filter_list = self.selectable_data_dict.get(FILTER_TERM, [])

        columns_that_need_unique_entries = {
            filter_dict[FIELD]
            for filter_dict in filter_list
            if filter_dict.get(USER_SELECTABLE)
        }

        if columns_that_need_unique_entries:
            self.unique_entry_dict = self.get_column_unique_entries(
                columns_that_need_unique_entries
            )

        for index, filter_dict in enumerate(filter_list):
            if filter_dict.get(USER_SELECTABLE):
                column = filter_dict[FIELD]
                selector_entries = self.unique_entry_dict.get(column, [])
                # append show_all_rows to the front of the list
                # dictionary in the format for make_filter_dict
                temp_dict = {
                    OPTION_COL: column,
                    ACTIVE_SELECTORS: filter_dict.get(ENTRIES, [SHOW_ALL_ROW]),
                    MULTIPLE: True,
                }
                if selector_entries:
                    selector_entries.sort()
                    selector_entries.insert(0, SHOW_ALL_ROW)
                    self.select_info.append(
                        make_filter_dict(FILTER, temp_dict, index, selector_entries)
                    )
                else:
                    html_filter_dict = make_filter_dict(FILTER, temp_dict, index)
                    # allow a free text box if there are no selections
                    html_filter_dict[JINJA_SELECT_HTML_FILE] = AVAILABLE_SELECTORS[
                        MATCH
                    ][SELECT_HTML_TEMPLATE]
                    self.select_info.append(html_filter_dict)

        filter_range_list = self.selectable_data_dict.get(FILTER_RANGE, [])
        for index, filter_range_dict in enumerate(filter_range_list):
            if filter_range_dict.get(USER_SELECTABLE):
                if not schema:
                    schema = self.get_schema_for_data_source()
                column = filter_range_dict[FIELD]
                temp_dict = {
                    OPTION_COL: column,
                    ACTIVE_SELECTORS: filter_range_dict.get(VALUE, 0),
                    TYPE: DATETIME if schema[column] == DATE else NUMBER,
                }
                html_filter_dict = make_filter_dict(FILTER_RANGE, temp_dict, index)
                html_filter_dict[OPERATION] = filter_range_dict[OPERATION]
                self.select_info.append(html_filter_dict)


class ElasticSearchDataInventory(ElasticSearchHandler):
    @staticmethod
    def get_available_data_sources():
        """
        Lists all data sources available in the db
        :return:
        """
        return [
            table_name for table_name in current_app.es.indices.get_alias("*").keys()
        ]
