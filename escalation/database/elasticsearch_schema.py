from database.data_schema import DataConfigInterfaceBuilder

from utility.constants import *
from utility.schema_utils import conditional_dict, SchemaDataHolder


class ElasticSearchConfigInterfaceBuilder(DataConfigInterfaceBuilder):
    @staticmethod
    def build_data_sources_schema(data_source_names, possible_column_names):
        data_sources_schema = {
            "type": "object",
            TITLE: "Data Sources",
            "description": "Define which data tables are used in this graphic,"
            " and on which columns the data tables are joined",
            "required": [MAIN_DATA_SOURCE],
            OPTIONS: {DISABLE_COLLAPSE: True, DISABLE_PROPERTIES: True},
            PROPERTIES: {
                MAIN_DATA_SOURCE: {
                    TITLE: "Main Data Source",
                    "id": MAIN_DATA_SOURCE,
                    "type": "object",
                    "additionalProperties": False,
                    REQUIRED: [DATA_SOURCE_TYPE],
                    PROPERTIES: {
                        DATA_SOURCE_TYPE: {
                            "type": "string",
                            TITLE: "Data Source Type",
                            **conditional_dict(ENUM, data_source_names),
                        },
                    },
                    OPTIONS: {DISABLE_COLLAPSE: True, DISABLE_PROPERTIES: True},
                },
                ADDITIONAL_DATA_SOURCES: {
                    "type": "array",
                    TITLE: "Additional Data Sources",
                    ITEMS: {
                        "type": "object",
                        TITLE: "Additional Data Source",
                        "additionalProperties": False,
                        "id": ADDITIONAL_DATA_SOURCES,
                        REQUIRED: [DATA_SOURCE_TYPE],
                        OPTIONS: {DISABLE_COLLAPSE: True, DISABLE_PROPERTIES: True},
                        PROPERTIES: {
                            DATA_SOURCE_TYPE: {
                                "type": "string",
                                TITLE: "Data Source Type",
                                **conditional_dict(ENUM, data_source_names),
                            },
                        },
                    },
                },
            },
        }
        return data_sources_schema

    def build_data_filter_schema(self):
        filter_term = {
            TYPE: ARRAY_STRING,
            TITLE: "Term query",
            DESCRIPTION: "Returns documents that contain an exact term (or one or more terms) in a provided field.",
            ITEMS: {
                TYPE: OBJECT,
                REQUIRED: [FIELD, ENTRIES],
                ID: "filter_item",
                PROPERTIES: {
                    FIELD: {
                        TYPE: STRING,
                        TITLE: "Field",
                        DESCRIPTION: "Field you wish to filter on",
                        **conditional_dict(ENUM, self.data_holder.filter_dict[FILTER]),
                    },
                    ENTRIES: {
                        TYPE: ARRAY_STRING,
                        MIN_ITEMS: 1,
                        ITEMS: {
                            TYPE: STRING,
                            **(
                                {
                                    ANYOF: [
                                        {
                                            TITLE: "Dropdown",
                                            "watch": {
                                                COLUMN_NAME: ".".join(
                                                    ["filter_item", FIELD]
                                                )
                                            },
                                            "enumSource": [
                                                {
                                                    "source": self.data_holder.unique_entry_values_list,
                                                    "filter": COLUMN_VALUE_FILTER,
                                                    "title": CALLBACK,
                                                    "value": CALLBACK,
                                                }
                                            ],
                                        },
                                        {TITLE: "Text box"},
                                    ]
                                }
                                if self.data_holder.unique_entry_values_list
                                else {}
                            ),
                        },
                    },
                    USER_SELECTABLE: self.user_selectable_dict,
                },
            },
        }
        filter_range = {
            TYPE: ARRAY_STRING,
            TITLE: "Range query",
            DESCRIPTION: "Returns documents that contain terms within a provided range.",
            ITEMS: {
                TYPE: OBJECT,
                REQUIRED: [FIELD, OPERATION, VALUE],
                PROPERTIES: {
                    FIELD: {
                        TYPE: STRING,
                        TITLE: "Field",
                        DESCRIPTION: "Field you wish to filter on",
                        **conditional_dict(
                            ENUM,
                            self.data_holder.filter_dict[NUMERICAL_FILTER]
                            + self.data_holder.filter_dict[DATE],
                        ),
                    },
                    OPERATION: {
                        TYPE: STRING,
                        ENUM: ["lte", "lt", "gt", "gte"],
                        OPTIONS: {
                            "enum_titles": [
                                "Less than or equal to",
                                "Less than",
                                "Greater than or equal to",
                                "Greater than",
                            ]
                        },
                    },
                    VALUE: {
                        ONEOF: [
                            {TYPE: "number"},
                            {TYPE: "string", "format": "datetime-local",},
                            {
                                TYPE: "string",
                                TITLE: "Time Delta",
                                PATTERN: "^now([-\\+][0-9]+[yMwdhHms](\\/[yMwdhHms])?)?$",
                                DEFAULT: "now-1d",
                                DESCRIPTION: "For example: *now-1d*."
                                " See https://www.elastic.co/guide/en/elasticsearch/reference/7.13/common-options.html#date-math",
                            },
                        ],
                    },
                    USER_SELECTABLE: self.user_selectable_dict,
                    TYPE: {
                        TYPE: "string",
                        DESCRIPTION: "number or datetime, needed if adding a data selector on the dashboard",
                        DEFAULT: "number",
                        ENUM: ["number", DATETIME],
                    },
                },
            },
        }
        selectable_data_schema = {
            TYPE: OBJECT,
            TITLE: "Elasticsearch options",
            DESCRIPTION: "https://www.elastic.co/guide/en/elasticsearch/reference/current/search-your-data.html.",
            ADDITIONAL_PROPERTIES: False,
            OPTIONS: {REMOVE_EMPTY_PROPERTIES: True,},
            DEFAULT_PROPERTIES: [SIZE],
            PROPERTIES: {
                FROM: {
                    TYPE: INTEGER,
                    TITLE: "From",
                    DESCRIPTION: "The number of hits to skip.",
                    MINIMUM: 0,
                    DEFAULT: 0,
                },
                SIZE: {
                    TITLE: "Size",
                    TYPE: INTEGER,
                    DESCRIPTION: "The maximum number of hits to return.",
                    MINIMUM: 0,
                    DEFAULT: 50,
                },
                SORT: {
                    TYPE: ARRAY_STRING,
                    TITLE: "Sort",
                    DESCRIPTION: "Allows you to add one or more sorts on specific fields. Each sort can be reversed"
                    " as well. The sort is defined on a per field level, with special field name"
                    " for _score to sort by score, and _doc to sort by index order.",
                    ITEMS: {
                        TYPE: OBJECT,
                        REQUIRED: [FIELD],
                        PROPERTIES: {
                            FIELD: {
                                TYPE: STRING,
                                **conditional_dict(
                                    ENUM,
                                    self.data_holder.possible_column_names,
                                    ["_score", "_doc"],
                                ),
                            },
                            "order": {TYPE: STRING, ENUM: ["asc", "desc"]},
                            "mode": {
                                TYPE: STRING,
                                DESCRIPTION: "Elasticsearch supports sorting by array or multi-valued fields. The mode"
                                " option controls what array value is picked for sorting the document"
                                " it belongs to.",
                                ENUM: ["min", "max", "sum", "avg", "median"],
                            },
                        },
                    },
                },
                FILTER_TERM: filter_term,
                FILTER_RANGE: filter_range,
                MATCH: {
                    TYPE: ARRAY_STRING,
                    TITLE: "Match (Multi-Match) query",
                    DESCRIPTION: "https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html",
                    ITEMS: {
                        TYPE: OBJECT,
                        DESCRIPTION: "Returns documents that match a provided text, number, date or boolean value. The "
                        "provided text is analyzed before matching. Put in one field for match and multiple "
                        "fields for multi-match.",
                        REQUIRED: [FIELDS, QUERY],
                        DEFAULT_PROPERTIES: [FIELDS, QUERY],
                        PROPERTIES: {
                            FIELDS: {
                                TYPE: ARRAY_STRING,
                                MIN_ITEMS: 1,
                                ITEMS: {
                                    TYPE: STRING,
                                    TITLE: "Field",
                                    DESCRIPTION: "Field you wish to search",
                                    **conditional_dict(
                                        ENUM, self.data_holder.filter_dict[TEXT]
                                    ),
                                },
                            },
                            QUERY: {
                                DESCRIPTION: "Text, number, boolean value or date you wish to find "
                                "in the provided field(s)",
                                ANYOF: [
                                    {TYPE: STRING, TITLE: TEXT},
                                    {
                                        TYPE: STRING,
                                        TITLE: DATETIME,
                                        "format": "datetime-local",
                                    },
                                    {TYPE: NUMBER},
                                    {TYPE: BOOLEAN},
                                ],
                            },
                            USER_SELECTABLE: self.user_selectable_dict,
                            "fuzziness": {
                                TYPE: STRING,
                                DESCRIPTION: "Maximum edit distance allowed for matching.",
                                DEFAULT: "AUTO",
                            },
                            "max_expansions": {
                                TYPE: INTEGER,
                                DESCRIPTION: "Maximum number of terms to which the query will expand.",
                                MINIMUM: 0,
                                DEFAULT: 50,
                            },
                            "prefix_length": {
                                TYPE: INTEGER,
                                DESCRIPTION: "Number of beginning characters left unchanged for fuzzy matching.",
                                MINIMUM: 0,
                                DEFAULT: 50,
                            },
                            "operator": {
                                TYPE: STRING,
                                DESCRIPTION: "Boolean logic used to interpret text in the query value. OR - "
                                "For example, a query value of capital of Hungary is interpreted as capital "
                                "OR of OR Hungary. AND - For example, a query value of capital of Hungary is "
                                "interpreted as capital AND of AND Hungary."
                                " Recommended not to use with multiple fields.",
                                ENUM: ["OR", "AND"],
                                DEFAULT: "OR",
                            },
                            "minimum_should_match": {
                                TYPE: STRING,
                                DESCRIPTION: "Minimum number of clauses that must match for a document to be returned. "
                                "Recommended not to use with multiple fields.",
                                DEFAULT: "1",
                            },
                            TYPE: {
                                TYPE: STRING,
                                DESCRIPTION: "For multiple fields."
                                " See https://www.elastic.co/guide/en/elasticsearch/reference/7.12/query-dsl-multi-match-query.html#multi-match-types.",
                                ENUM: [
                                    "best_fields",
                                    "most_fields",
                                    "cross_fields",
                                    "phrase",
                                    "phrase_prefix",
                                    "bool_prefix",
                                ],
                                DEFAULT: "best_fields",
                            },
                            TIE_BREAKER: {
                                DESCRIPTION: "Used with multiple fields and *type* equal to cross_field or best_fields."
                                "e.g. normally the best_fields type uses the score of the single best matching field, "
                                "but if tie_breaker is specified, then it calculates the score as the score from the "
                                "best matching field plus tie_breaker * _score for all other matching fields",
                                TYPE: NUMBER,
                                MINIMUM: 0,
                                MAXIMUM: 1,
                                DEFAULT: 0,
                            },
                        },
                    },
                },
                AGGREGATIONS: {
                    DESCRIPTION: "This differs from the Elasticsearch documentation. You specify one or more terms "
                    "and (date) histogram bucket aggregations and then a metric aggregation. All columns"
                    " in the visualization need to be specified as a bucket or choose *doc_count* if no metric is"
                    " specified. ",
                    TYPE: OBJECT,
                    REQUIRED: [METRIC, METRIC_FIELD, BUCKETS],
                    PROPERTIES: {
                        BUCKETS: {
                            TYPE: ARRAY_STRING,
                            MIN_ITEMS: 1,
                            ITEMS: {
                                ONEOF: [
                                    {
                                        TITLE: "Terms aggregation",
                                        TYPE: OBJECT,
                                        REQUIRED: [AGG_TYPE, FIELD],
                                        DEFAULT_PROPERTIES: [FIELD],
                                        PROPERTIES: {
                                            AGG_TYPE: {
                                                TITLE: "Aggregation Type",
                                                TYPE: STRING,
                                                ENUM: [TERMS_AGGREGATION],
                                                OPTIONS: {HIDDEN: True},
                                            },
                                            FIELD: {
                                                TYPE: STRING,
                                                **conditional_dict(
                                                    ENUM,
                                                    self.data_holder.filter_dict[
                                                        FILTER
                                                    ],
                                                ),
                                            },
                                            SIZE: {
                                                DESCRIPTION: "Set to define how many term buckets should be returned"
                                                " out of the overall terms list.",
                                                TYPE: INTEGER,
                                                MINIMUM: 1,
                                                DEFAULT: 10,
                                            },
                                            INCLUDE: {
                                                ONEOF: [
                                                    {
                                                        DESCRIPTION: "Regular expression of what to include.",
                                                        TYPE: STRING,
                                                        TITLE: "RegEx",
                                                    },
                                                    {
                                                        TITLE: "Word List",
                                                        TYPE: ARRAY_STRING,
                                                        DESCRIPTION: "Array of strings to include.",
                                                        ITEMS: {TYPE: STRING},
                                                    },
                                                ]
                                            },
                                            EXCLUDE: {
                                                ONEOF: [
                                                    {
                                                        DESCRIPTION: "Regular expression of what to exclude.",
                                                        TYPE: STRING,
                                                        TITLE: "RegEx",
                                                    },
                                                    {
                                                        TITLE: "Word List",
                                                        TYPE: ARRAY_STRING,
                                                        DESCRIPTION: "Array of strings to exclude.",
                                                        ITEMS: {TYPE: STRING},
                                                    },
                                                ]
                                            },
                                        },
                                    },
                                    {
                                        TITLE: "Histogram aggregation",
                                        TYPE: OBJECT,
                                        REQUIRED: [AGG_TYPE, FIELD, INTERVAL],
                                        PROPERTIES: {
                                            AGG_TYPE: {
                                                TITLE: "Aggregation Type",
                                                TYPE: STRING,
                                                ENUM: [HISTOGRAM_AGGREGATION],
                                                OPTIONS: {HIDDEN: True},
                                            },
                                            FIELD: {
                                                TITLE: FIELD,
                                                TYPE: STRING,
                                                **conditional_dict(
                                                    ENUM,
                                                    self.data_holder.filter_dict[
                                                        NUMERICAL_FILTER
                                                    ],
                                                ),
                                            },
                                            INTERVAL: {
                                                DESCRIPTION: "Fixed size of the buckets over the values",
                                                TYPE: NUMBER,
                                                MINIMUM: 0,
                                            },
                                            MIN_DOC_COUNT: {
                                                DESCRIPTION: "By default the response will fill gaps in the histogram"
                                                " with empty buckets. It is possible change that and"
                                                " request buckets with a higher minimum count thanks to the"
                                                " min_doc_count setting",
                                                TYPE: INTEGER,
                                                MINIMUM: 0,
                                                DEFAULT: 0,
                                            },
                                        },
                                    },
                                    {
                                        TITLE: "Date Histogram aggregation",
                                        TYPE: OBJECT,
                                        REQUIRED: [AGG_TYPE, FIELD, INTERVAL, UNITS],
                                        PROPERTIES: {
                                            AGG_TYPE: {
                                                TITLE: "Aggregation Type",
                                                TYPE: STRING,
                                                ENUM: [DATE_HISTOGRAM_AGGREGATION],
                                                OPTIONS: {HIDDEN: True},
                                            },
                                            FIELD: {
                                                TITLE: FIELD,
                                                TYPE: STRING,
                                                **conditional_dict(
                                                    ENUM,
                                                    self.data_holder.filter_dict[DATE],
                                                ),
                                            },
                                            INTERVAL: {
                                                DESCRIPTION: "Fixed size of the buckets over the values in *units*",
                                                TYPE: INTEGER,
                                                DEFAULT: 1,
                                                MINIMUM: 0,
                                            },
                                            UNITS: {
                                                DESCRIPTION: "SI units",
                                                TYPE: STRING,
                                                ENUM: ["ms", "s", "m", "h", "d"],
                                                DEFAULT: "h",
                                                OPTIONS: {
                                                    "enum_titles": [
                                                        "milliseconds",
                                                        "seconds",
                                                        "minutes",
                                                        "hours",
                                                        "days",
                                                    ]
                                                },
                                            },
                                        },
                                    },
                                ]
                            },
                        },
                        METRIC: {
                            TYPE: STRING,
                            DESCRIPTION: "single-value numeric metrics aggregation over the buckets",
                            ENUM: ["count", "avg", "sum", "min", "max"],
                        },
                        METRIC_FIELD: {
                            TYPE: STRING,
                            DESCRIPTION: "If metric is not count, what field to perform the aggregation over."
                            " If using count this value does not matter",
                            **conditional_dict(
                                ENUM, self.data_holder.filter_dict[NUMERICAL_FILTER],
                            ),
                        },
                        SORT_ORDER: {
                            TYPE: STRING,
                            ENUM: ["asc", "desc"],
                            DEFAULT: "desc",
                        },
                    },
                },
                # SIGNIFICANT_TERMS: { # these are not implemeneted in the handler side
                #    DESCRIPTION: "Performs the significant terms_aggregation. Cannot be used with aggregations or"
                #    " significant text. Must"
                #    " be used with either filter_terms, filter_range or filter_match.",
                #    TYPE: OBJECT,
                #    REQUIRED: [FIELD],
                #    PROPERTIES: {
                #        FIELD: {
                #            TYPE: STRING,
                #            **conditional_dict(
                #                ENUM, self.data_holder.filter_dict[FILTER],
                #            ),
                #        },
                #        BACKGROUND_.format(FILTER_TERM): filter_term,
                #        BACKGROUND_.format(FILTER_RANGE): filter_range,
                #    },
                # },
                # SIGNIFICANT_TEXT: {
                #    DESCRIPTION: "Performs the significant text aggregation. Cannot be used with aggregations or"
                #    " significant_terms. Must"
                #    " be used with either filter_terms, filter_range or filter_match.",
                #    TYPE: OBJECT,
                #    REQUIRED: [FIELD],
                #    PROPERTIES: {
                #        FIELD: {
                #            TYPE: STRING,
                #            **conditional_dict(
                #                ENUM, self.data_holder.filter_dict[FILTER],
                #            ),
                #        },
                #        BACKGROUND_.format(FILTER_TERM): filter_term,
                #        BACKGROUND_.format(FILTER_RANGE): filter_range,
                #        FILTER_DUPLICATE_TEXT: {TYPE: BOOLEAN, DEFAULT: False},
                #    },
                # },
            },
        }
        return selectable_data_schema
