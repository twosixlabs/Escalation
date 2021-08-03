# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import json
from types import MappingProxyType

import pytest
from flask import current_app

from elasticsearch import helpers

from app_setup import create_app, configure_backend
from database.elasticsearch_handler import (
    ElasticSearchHandler,
    ElasticSearchDataInventory,
    get_keys_and_types,
)
from utility.constants import (
    APP_CONFIG_JSON,
    TEST_APP_DEPLOY_DATA,
    CONFIG_FILE_FOLDER,
    MAIN_DATA_SOURCE,
    DATA_SOURCE_TYPE,
    FROM,
    SIZE,
    FIELD,
    SORT,
    ENTRIES,
    FILTER_TERM,
    VALUE,
    OPERATION,
    FILTER_RANGE,
    MATCH,
    FIELDS,
    QUERY,
    AGGREGATIONS,
    BUCKETS,
    TERMS_AGGREGATION,
    METRIC,
    METRIC_FIELD,
    DOC_COUNT,
    AGG_TYPE,
    PROPERTIES,
    TYPE,
    FIELD_DATA,
    USER_SELECTABLE,
    SHOW_ALL_ROW,
)

PENGUIN_SIZE = "penguin_size"
PENGUIN_SIZE_SMALL = "penguin_size_small"

SEX = "sex"
ISLAND = "island"
BODY_MASS = "body_mass_g"
CULMEN_LENGTH = "culmen_length_mm"
CULMEN_DEPTH = "culmen_depth_mm"
FLIPPER_LENGTH = "flipper_length_mm"


@pytest.fixture()
def test_app_client_es_backed(main_json_es_backend_fixture):
    # set an env other than DEVELOPMENT, which is used as a gate for some features
    flask_app = create_app(env="testing")
    flask_app.config[APP_CONFIG_JSON] = MappingProxyType(main_json_es_backend_fixture)
    flask_app.config[CONFIG_FILE_FOLDER] = TEST_APP_DEPLOY_DATA
    configure_backend(flask_app)
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    # application context needs to be pushed to be able to handle GETs and POSTs
    ctx.push()
    # provide the testing client to the tests
    yield testing_client  # this is where the testing happens!
    # remove the context to clean up the test environment
    ctx.pop()


@pytest.fixture()
def rebuild_elasticsearch_database(test_app_client_es_backed):
    es = current_app.es
    es.indices.delete(index="_all", ignore=[400, 404])
    with open("test_app_deploy_data/es_data/accounts/accounts.json", "r") as file:
        data = json.load(file)
    for a_data in data[:3]:
        es.index(index="small-accounts", body=a_data, params={"refresh": "true"})
    actions = [{"_index": "accounts", "_source": a_data} for a_data in data]
    helpers.bulk(es, actions, params={"refresh": "true"})


@pytest.fixture()
def get_es_fixture(rebuild_elasticsearch_database):
    data_sources = {
        MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "accounts"},
    }
    es_handler = ElasticSearchHandler(data_sources)
    return es_handler


@pytest.fixture()
def get_es_fixture_small(rebuild_elasticsearch_database):
    data_sources = {
        MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "small-accounts"},
    }
    es_handler = ElasticSearchHandler(data_sources)
    return es_handler


def test_es_handler_init(get_es_fixture):
    assert "accounts" == get_es_fixture.main_data_source


def test_get_column_data_no_filter(get_es_fixture_small):
    data_set = {
        "firstname",
        "lastname",
        "assets.stocks",
    }
    test_dict = get_es_fixture_small.get_column_data(data_set)
    assert test_dict["firstname"] == ["Amber", "Hattie", "Nanette"]
    assert test_dict["lastname"] == ["Duke", "Bond", "Bates"]
    assert test_dict["assets.stocks"] == [15574, 86936, 93390]


def test_get_column_data_records(get_es_fixture_small):
    data_set = {
        "firstname",
        "lastname",
        "assets.stocks",
    }
    test_dict = get_es_fixture_small.get_column_data(data_set, "records")
    expected_list = [
        {"firstname": ["Amber"], "lastname": ["Duke"], "assets.stocks": [15574]},
        {"firstname": ["Hattie"], "lastname": ["Bond"], "assets.stocks": [86936]},
        {"firstname": ["Nanette"], "lastname": ["Bates"], "assets.stocks": [93390]},
    ]
    assert expected_list == test_dict


def test_get_column_from_size(get_es_fixture_small):
    selectable_data_dict = {FROM: 1, SIZE: 1}
    get_es_fixture_small.selectable_data_dict = selectable_data_dict
    data_set = {"firstname"}
    test_dict = get_es_fixture_small.get_column_data(data_set)
    assert test_dict["firstname"] == ["Hattie"]


def test_get_column_sort(get_es_fixture_small):
    get_es_fixture_small.selectable_data_dict = {SORT: [{FIELD: "lastname.keyword"}]}
    data_set = {
        "firstname",
        "lastname",
    }
    test_dict = get_es_fixture_small.get_column_data(data_set)
    assert test_dict["firstname"] == ["Nanette", "Hattie", "Amber"]
    assert test_dict["lastname"] == ["Bates", "Bond", "Duke"]

    get_es_fixture_small.selectable_data_dict = {
        SORT: [{FIELD: "employer.keyword", "order": "desc"}]
    }
    data_set = {
        "firstname",
    }
    test_dict = get_es_fixture_small.get_column_data(data_set)
    assert test_dict["firstname"] == ["Nanette", "Amber", "Hattie"]


def test_get_column_data_filter(get_es_fixture_small):
    # also test apply filters to data
    get_es_fixture_small.selectable_data_dict = {
        FILTER_TERM: [{FIELD: "state.keyword", ENTRIES: ["VA"]}]
    }
    data_set = {
        "firstname",
        "lastname",
    }
    test_dict = get_es_fixture_small.get_column_data(data_set)
    assert test_dict["firstname"] == ["Nanette"]
    assert test_dict["lastname"] == ["Bates"]

    get_es_fixture_small.selectable_data_dict = {
        FILTER_TERM: [{FIELD: "state.keyword", ENTRIES: ["VA", "TN"]}]
    }
    test_dict = get_es_fixture_small.get_column_data(data_set)
    assert test_dict["firstname"] == ["Hattie", "Nanette"]
    assert test_dict["lastname"] == ["Bond", "Bates"]


def test_get_column_data_numerical_filter(get_es_fixture_small):
    get_es_fixture_small.selectable_data_dict = {
        FILTER_RANGE: [{FIELD: "balance", OPERATION: "gte", VALUE: 10000}]
    }
    data_set = {
        "firstname",
        "lastname",
    }
    test_dict = get_es_fixture_small.get_column_data(data_set)

    assert test_dict["firstname"] == ["Amber", "Nanette"]
    assert test_dict["lastname"] == ["Duke", "Bates"]


def test_get_column_data_match(get_es_fixture_small):
    get_es_fixture_small.selectable_data_dict = {
        MATCH: [{FIELDS: ["address"], QUERY: "Bristol"}]
    }
    data_set = {"firstname", "lastname"}
    test_dict = get_es_fixture_small.get_column_data(data_set)

    assert test_dict["firstname"] == ["Hattie"]
    assert test_dict["lastname"] == ["Bond"]


def test_get_column_data_numerical_filter_datetime(get_es_fixture_small):
    assert False


def test_get_column_unique_entries(get_es_fixture_small):
    unique_entries = get_es_fixture_small.get_column_unique_entries({"state"})
    assert isinstance(unique_entries["state"], list)
    assert set(unique_entries["state"]) == {"IL", "VA", "TN"}


def test_get_available_data_sources(rebuild_elasticsearch_database):
    file_names = ElasticSearchDataInventory.get_available_data_sources()
    assert "small-accounts" in file_names
    assert "accounts" in file_names
    assert len(file_names) == 2


def test_get_keys_and_types():
    expected_column_type_dict = {
        "key1.key2.key3.key4.key5": {TYPE: "long"},
        "key1.key2.key3_the_second": {FIELD_DATA: False, TYPE: "text"},
    }
    test_mapper = {
        "key1": {
            PROPERTIES: {
                "key2": {
                    PROPERTIES: {
                        "key3": {
                            PROPERTIES: {"key4": {PROPERTIES: {"key5": {TYPE: "long"}}}}
                        },
                        "key3_the_second": {TYPE: "text"},
                    }
                }
            }
        }
    }
    col_type_dict = get_keys_and_types(test_mapper)
    assert expected_column_type_dict == col_type_dict


def test_get_column_names_for_data_source(get_es_fixture):
    column_names = get_es_fixture.get_column_names_for_data_source()
    expected_column_names = {
        "account_number",
        "address",
        "address.keyword",
        "age",
        "assets.house",
        "assets.stocks",
        "balance",
        "city",
        "city.keyword",
        "email",
        "email.keyword",
        "employer",
        "employer.keyword",
        "firstname",
        "firstname.keyword",
        "gender",
        "gender.keyword",
        "lastname",
        "lastname.keyword",
        "state",
        "state.keyword",
        DOC_COUNT,
    }

    assert set(column_names) == expected_column_names


def test_get_column_data_with_aggregation(get_es_fixture):
    expected_result = {
        "state.keyword": ["TX", "MD", "MA", "TN", "ID", "IL", "AL", "ND", "OK", "NC"],
        "balance": [
            782199.0,
            732523.0,
            710408.0,
            709135.0,
            657957.0,
            648774.0,
            643489.0,
            637856.0,
            610295.0,
            597781.0,
        ],
    }
    data_set = {"state.keyword", "balance"}
    get_es_fixture.selectable_data_dict = {
        AGGREGATIONS: {
            BUCKETS: [{AGG_TYPE: TERMS_AGGREGATION, FIELD: "state.keyword"}],
            METRIC: "sum",
            METRIC_FIELD: "balance",
        }
    }

    test_dict = get_es_fixture.get_column_data(data_set)

    assert expected_result == test_dict

    expected_result = {
        "state.keyword": ["TX", "MD", "ID", "AL", "ME", "TN", "WY", "DC", "MA", "ND"],
        "doc_count": [30, 28, 27, 25, 25, 25, 25, 24, 24, 24],
    }

    get_es_fixture.selectable_data_dict = {
        AGGREGATIONS: {
            BUCKETS: [{AGG_TYPE: TERMS_AGGREGATION, FIELD: "state.keyword"}],
            METRIC: "count",
            METRIC_FIELD: "balance",
        }
    }

    test_dict = get_es_fixture.get_column_data({"state.keyword"})

    assert expected_result == test_dict

    expected_result = {
        "state.keyword": ["WA", "IL", "MS", "AL", "NH", "MO"],
        "gender.keyword": ["M", "M", "M", "F", "F", "F",],
        "balance": [49989.0, 49568.0, 49567.0, 49795.0, 49741.0, 49671.0],
    }

    get_es_fixture.selectable_data_dict = {
        AGGREGATIONS: {
            BUCKETS: [
                {AGG_TYPE: TERMS_AGGREGATION, FIELD: "gender.keyword"},
                {AGG_TYPE: TERMS_AGGREGATION, FIELD: "state.keyword", SIZE: 3},
            ],
            METRIC: "max",
            METRIC_FIELD: "balance",
        }
    }

    test_dict = get_es_fixture.get_column_data(
        {"state.keyword", "gender.keyword", "balance"}
    )

    assert expected_result == test_dict


def test_add_active_selectors_to_selectable_data_dict(get_es_fixture):
    get_es_fixture.selectable_data_dict = {
        FILTER_TERM: [
            {FIELD: "gender.keyword", ENTRIES: ["M"], USER_SELECTABLE: True},
            {FIELD: "state.keyword", ENTRIES: ["IL", "VA"], USER_SELECTABLE: True},
        ],
        FILTER_RANGE: [
            {FIELD: "balance", OPERATION: "gte", VALUE: 10000, USER_SELECTABLE: True}
        ],
        MATCH: [{FIELDS: ["state"], QUERY: "FL", USER_SELECTABLE: True}],
    }
    get_es_fixture.addendum_dict = {
        "filter_0": [SHOW_ALL_ROW],
        "filter_1": ["NJ", "VA"],
        "filter_range_0": [3000],
        "match_0": ["FL MI"],
    }
    get_es_fixture.add_active_selectors_to_selectable_data_dict()

    assert get_es_fixture.selectable_data_dict[FILTER_TERM][0][ENTRIES] == [
        SHOW_ALL_ROW
    ]
    assert get_es_fixture.selectable_data_dict[FILTER_TERM][1][ENTRIES] == ["NJ", "VA"]
    assert get_es_fixture.selectable_data_dict[FILTER_RANGE][0][VALUE] == 3000
    assert get_es_fixture.selectable_data_dict[MATCH][0][QUERY] == "FL MI"


def test_create_data_subselect_info_for_plot(get_es_fixture):
    get_es_fixture.selectable_data_dict = {
        FILTER_TERM: [
            {FIELD: "gender.keyword", ENTRIES: ["M"], USER_SELECTABLE: True},
            {FIELD: "state.keyword", ENTRIES: ["IL", "VA"], USER_SELECTABLE: True},
        ],
        FILTER_RANGE: [
            {FIELD: "balance", OPERATION: "gte", VALUE: 10000, USER_SELECTABLE: True}
        ],
        MATCH: [{FIELDS: ["state"], QUERY: "FL MI", USER_SELECTABLE: True}],
    }

    get_es_fixture.create_data_subselect_info_for_plot()
    expected_select_info = [
        {
            "type": "",
            "select_html_file": "match.html",
            "name": "match_0",
            "text": "Match in state",
            "active_selector": "FL MI",
            "multiple": False,
            "entries": None,
        },
        {
            "type": "",
            "select_html_file": "selector.html",
            "name": "filter_0",
            "text": "Filter by gender.keyword",
            "active_selector": ["M"],
            "multiple": True,
            "entries": ["Show All Rows", "F", "M"],
        },
        {
            "type": "",
            "select_html_file": "selector.html",
            "name": "filter_1",
            "text": "Filter by state.keyword",
            "active_selector": ["IL", "VA"],
            "multiple": True,
            "entries": [
                "Show All Rows",
                "AK",
                "AL",
                "AR",
                "AZ",
                "CA",
                "CO",
                "CT",
                "DC",
                "DE",
                "FL",
                "GA",
                "HI",
                "IA",
                "ID",
                "IL",
                "IN",
                "KS",
                "KY",
                "LA",
                "MA",
                "MD",
                "ME",
                "MI",
                "MN",
                "MO",
                "MS",
                "MT",
                "NC",
                "ND",
                "NE",
                "NH",
                "NJ",
                "NM",
                "NV",
                "NY",
                "OH",
                "OK",
                "OR",
                "PA",
                "RI",
                "SC",
                "SD",
                "TN",
                "TX",
                "UT",
                "VA",
                "VT",
                "WA",
                "WI",
                "WV",
                "WY",
            ],
        },
        {
            "type": "number",
            "select_html_file": "filter_range.html",
            "name": "filter_range_0",
            "text": "Filter by balance",
            "active_selector": 10000,
            "multiple": False,
            "entries": None,
            "operation": "gte",
        },
    ]

    assert expected_select_info == get_es_fixture.select_info
