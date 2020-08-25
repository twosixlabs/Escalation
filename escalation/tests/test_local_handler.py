# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

from flask import current_app
import pandas as pd

from database.local_handler import LocalCSVHandler, LocalCSVDataInventory
from utility.constants import (
    DATA_LOCATION,
    DATA_SOURCE_TYPE,
    MAIN_DATA_SOURCE,
    ADDITIONAL_DATA_SOURCES,
)


def test_local_handler_init(local_handler_fixture_small):
    data_sources = local_handler_fixture_small.data_sources
    assert len(data_sources) == 1
    main_data_source = data_sources[MAIN_DATA_SOURCE]
    assert main_data_source[DATA_LOCATION] == [
        "test_app_deploy_data/data/penguin_size_small/penguin_size_small.csv"
    ]
    # todo: more complicated init with key joining


def test_get_column_data(local_handler_fixture_small):
    data_dict = [
        "penguin_size_small:body_mass_g",
        "penguin_size_small:flipper_length_mm",
    ]
    test_dict = local_handler_fixture_small.get_column_data(data_dict)
    assert (test_dict["penguin_size_small:body_mass_g"] == [3750, 3800, 3250]).all()
    assert (test_dict["penguin_size_small:flipper_length_mm"] == [181, 186, 195]).all()

    test_dict = local_handler_fixture_small.get_column_data(
        data_dict,
        [{"type": "filter", "column": "penguin_size_small:sex", "selected": ["MALE"]}],
    )
    assert (test_dict["penguin_size_small:body_mass_g"] == [3750]).all()
    assert (test_dict["penguin_size_small:flipper_length_mm"] == [181]).all()

    test_dict = local_handler_fixture_small.get_column_data(
        data_dict,
        [
            {
                "type": "numerical_filter",
                "column": "penguin_size_small:body_mass_g",
                "operation": ">",
                "value": 3250,
            }
        ],
    )

    assert (test_dict["penguin_size_small:body_mass_g"] == [3750, 3800]).all()
    assert (test_dict["penguin_size_small:flipper_length_mm"] == [181, 186]).all()


def test_get_column_unique_entries(local_handler_fixture_small):
    unique_dict = local_handler_fixture_small.get_column_unique_entries(
        ["penguin_size_small:sex", "penguin_size_small:island"]
    )
    assert "MALE" in unique_dict["penguin_size_small:sex"]
    assert "FEMALE" in unique_dict["penguin_size_small:sex"]
    assert "Torgersen" in unique_dict["penguin_size_small:island"]


# define 2 joined data tables as the data_source
TWO_DATA_SOURCES_CONFIG = {
    MAIN_DATA_SOURCE: {"data_source_type": "penguin_size"},
    ADDITIONAL_DATA_SOURCES: [
        {
            "data_source_type": "mean_penguin_stat",
            "join_keys": [
                ("penguin_size:study_name", "mean_penguin_stat:study_name"),
                ("penguin_size:sex", "mean_penguin_stat:sex"),
                ("penguin_size:species", "mean_penguin_stat:species"),
            ],
        }
    ],
}


def test_init(test_app_client):
    handler = LocalCSVHandler(data_sources=TWO_DATA_SOURCES_CONFIG)
    # test that init gets the correct file for each data source folder
    assert handler.data_sources[MAIN_DATA_SOURCE][DATA_LOCATION] == [
        "test_app_deploy_data/data/penguin_size/penguin_size.csv",
        "test_app_deploy_data/data/penguin_size/penguin_size_2.csv",
    ]
    assert handler.data_sources[ADDITIONAL_DATA_SOURCES][0][DATA_LOCATION] == [
        "test_app_deploy_data/data/mean_penguin_stat/mean_penguin_stat.csv"
    ]


def test_build_combined_data_table(test_app_client):
    handler = LocalCSVHandler(data_sources=TWO_DATA_SOURCES_CONFIG)
    penguin_size = pd.concat(
        [
            pd.read_csv("test_app_deploy_data/data/penguin_size/penguin_size.csv"),
            pd.read_csv("test_app_deploy_data/data/penguin_size/penguin_size_2.csv"),
        ]
    )
    num_rows_in_leftmost_table = penguin_size.shape[0]
    num_rows_in_combined_table = handler.combined_data_table.shape[0]
    # this is a left join, so assuming only one matching key in right table per key in left,
    # the number of rows of final table should equal the left/first table
    assert num_rows_in_leftmost_table == num_rows_in_combined_table
    # todo: one to many join, where we expect the number of rows to change


def test_build_combined_data_table_with_filtered_data_source(test_app_client):
    current_app.config.active_data_source_filters = {
        "penguin_size": ["test_app_deploy_data/data/penguin_size/penguin_size.csv"]
    }
    handler = LocalCSVHandler(data_sources=TWO_DATA_SOURCES_CONFIG)
    # only the one included penguin size is loaded, not the second
    penguin_size = pd.read_csv(
        "test_app_deploy_data/data/penguin_size/penguin_size.csv"
    )
    num_rows_in_leftmost_table = penguin_size.shape[0]
    num_rows_in_combined_table = handler.combined_data_table.shape[0]
    # this is a left join, so assuming only one matching key in right table per key in left,
    # the number of rows of final table should equal the left/first table
    assert num_rows_in_leftmost_table == num_rows_in_combined_table
    # todo: one to many join, where we expect the number of rows to change


def test_get_available_data_sources(test_app_client):
    file_names = LocalCSVDataInventory.get_available_data_sources()
    assert "penguin_size_small" in file_names
    assert "penguin_size" in file_names
    assert "mean_penguin_stat" in file_names


def test_get_schema_for_data_source(test_app_client):
    column_names = LocalCSVDataInventory(
        {MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "penguin_size"}}
    ).get_schema_for_data_source()
    expected_column_names = [
        "study_name",
        "species",
        "island",
        "sex",
        "region",
        "culmen_depth_mm",
        "culmen_length_mm",
        "flipper_length_mm",
        "body_mass_g",
    ]

    assert column_names == expected_column_names


def test_get_identifiers_for_data_source(test_app_client):
    file_names = LocalCSVDataInventory(
        {MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "penguin_size"}}
    ).get_identifiers_for_data_source()

    assert "test_app_deploy_data/data/penguin_size/penguin_size.csv" in file_names
    assert "test_app_deploy_data/data/penguin_size/penguin_size_2.csv" in file_names
