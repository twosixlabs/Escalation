# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

from collections import namedtuple
import numpy as np
import pandas as pd

from database.local_handler import LocalCSVHandler, LocalCSVDataInventory
from utility.constants import (
    DATA_LOCATION,
    DATA_SOURCE_TYPE,
    MAIN_DATA_SOURCE,
    ADDITIONAL_DATA_SOURCES,
    ACTIVE,
    INACTIVE,
    TABLE_NAME,
    UPLOAD_ID,
    UPLOAD_TIME,
    USERNAME,
    NOTES,
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


def test_init(test_app_client_csv_backed):
    handler = LocalCSVHandler(data_sources=TWO_DATA_SOURCES_CONFIG)
    # test that init gets the correct file for each data source folder
    assert handler.data_sources[MAIN_DATA_SOURCE][DATA_LOCATION] == [
        "test_app_deploy_data/data/penguin_size/penguin_size.csv",
        "test_app_deploy_data/data/penguin_size/penguin_size_2.csv",
    ]
    assert handler.data_sources[ADDITIONAL_DATA_SOURCES][0][DATA_LOCATION] == [
        "test_app_deploy_data/data/mean_penguin_stat/mean_penguin_stat.csv"
    ]


def test_build_combined_data_table(test_app_client_csv_backed):
    handler = LocalCSVHandler(data_sources=TWO_DATA_SOURCES_CONFIG)
    penguin_size = pd.concat(
        [
            pd.read_csv("test_app_deploy_data/data/penguin_size/penguin_size.csv"),
            pd.read_csv("test_app_deploy_data/data/penguin_size/penguin_size_2.csv"),
        ]
    )
    penguin_mean = pd.read_csv(
        "test_app_deploy_data/data/mean_penguin_stat/mean_penguin_stat.csv"
    )
    inner_join_table = pd.merge(
        penguin_size, penguin_mean, how="inner", on=["study_name", "sex", "species"]
    )
    num_rows_in_inner_table = inner_join_table.shape[0]
    num_rows_in_combined_table = handler.combined_data_table.shape[0]
    # this is a left join, so assuming only one matching key in right table per key in left,
    # the number of rows of final table should equal the left/first table
    assert num_rows_in_inner_table == num_rows_in_combined_table
    # todo: one to many join, where we expect the number of rows to change


def test_build_combined_data_table_with_filtered_data_source(
    test_app_client_csv_backed, mocker
):
    mock_metadata = pd.DataFrame(
        [
            {
                ACTIVE: False,
                TABLE_NAME: "penguin_size",
                UPLOAD_ID: "test_app_deploy_data/data/penguin_size/penguin_size_2.csv",
                UPLOAD_TIME: None,
                USERNAME: "Nick",
                NOTES: "test penguin size upload",
            }
        ]
    )

    mocker.patch(
        "database.local_handler.LocalCSVHandler.get_data_upload_metadata_df",
        return_value=mock_metadata,
    )
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


def test_get_available_data_sources(test_app_client_csv_backed):
    file_names = LocalCSVDataInventory.get_available_data_sources()
    assert "penguin_size_small" in file_names
    assert "penguin_size" in file_names
    assert "mean_penguin_stat" in file_names


def test_get_schema_for_data_source(test_app_client_csv_backed):
    column_names = LocalCSVHandler(
        {MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "penguin_size"}}
    ).get_schema_for_data_source()
    expected_column_names = [
        "penguin_size:study_name",
        "penguin_size:species",
        "penguin_size:island",
        "penguin_size:sex",
        "penguin_size:region",
        "penguin_size:culmen_depth_mm",
        "penguin_size:culmen_length_mm",
        "penguin_size:flipper_length_mm",
        "penguin_size:body_mass_g",
    ]

    assert set(column_names) == set(expected_column_names)


def test_get_data_upload_metadata(test_app_client_csv_backed):
    data_upload_metadata = LocalCSVDataInventory.get_data_upload_metadata(
        data_source_names=["penguin_size"]
    )

    expected_metadata = {
        "penguin_size": [
            # there is no corresponding metadata row for this file, so metadata is None
            {
                UPLOAD_ID: "penguin_size.csv",
                USERNAME: None,
                UPLOAD_TIME: None,
                ACTIVE: None,
                NOTES: None,
            },
            {
                UPLOAD_ID: "penguin_size_2.csv",
                USERNAME: "Nick",
                UPLOAD_TIME: "2020-09-01 12:05:02",
                ACTIVE: True,
                NOTES: "My second penguin data!",
            },
        ]
    }
    assert data_upload_metadata == expected_metadata


MOCK_METADATA = pd.DataFrame(
    [
        {
            ACTIVE: False,
            TABLE_NAME: "penguin_size",
            UPLOAD_ID: "test_app_deploy_data/data/penguin_size/penguin_size.csv",
            UPLOAD_TIME: None,
            USERNAME: "Nick",
            NOTES: "test penguin size upload 1",
        },
        {
            ACTIVE: True,
            TABLE_NAME: "penguin_size",
            UPLOAD_ID: "test_app_deploy_data/data/penguin_size/penguin_size_2.csv",
            UPLOAD_TIME: "2020-09-01 12:05:02",
            USERNAME: "Nick",
            NOTES: "test penguin size upload 2",
        },
    ]
)


def test_get_updated_metadata_df_write_no_change(test_app_client_csv_backed, mocker):
    # test that the metadata is unchanged if we don't update any active status
    mocker.patch(
        "database.local_handler.LocalCSVHandler.get_data_upload_metadata_df",
        return_value=MOCK_METADATA,
    )

    data_upload_metadata = LocalCSVDataInventory._get_updated_metadata_df_for_csv_write(
        data_source_name="penguin_size",
        active_data_dict={
            "test_app_deploy_data/data/penguin_size/penguin_size.csv": INACTIVE,
            "test_app_deploy_data/data/penguin_size/penguin_size_2.csv": ACTIVE,
        },
    )
    assert data_upload_metadata.equals(MOCK_METADATA)


def test_get_updated_metadata_df_write_active_change(
    test_app_client_csv_backed, mocker
):
    # test that the metadata shows an updated ACTIVE/INACTIVE status
    mocker.patch(
        "database.local_handler.LocalCSVHandler.get_data_upload_metadata_df",
        return_value=MOCK_METADATA,
    )

    data_upload_metadata = LocalCSVDataInventory._get_updated_metadata_df_for_csv_write(
        data_source_name="penguin_size",
        active_data_dict={
            "test_app_deploy_data/data/penguin_size/penguin_size.csv": ACTIVE,
            "test_app_deploy_data/data/penguin_size/penguin_size_2.csv": INACTIVE,
        },
    )
    expected_df = MOCK_METADATA.copy()
    expected_df.loc[0, ACTIVE] = True
    expected_df.loc[1, ACTIVE] = False
    assert data_upload_metadata.equals(expected_df)


def test_get_updated_metadata_df_write_for_file_not_yet_in_metadata(
    test_app_client_csv_backed, mocker
):
    # test that the metadata shows an updated ACTIVE/INACTIVE status
    mocker.patch(
        "database.local_handler.LocalCSVHandler.get_data_upload_metadata_df",
        return_value=MOCK_METADATA,
    )

    new_upload_id = "test_app_deploy_data/data/penguin_size/penguin_size_3.csv"
    data_upload_metadata = LocalCSVDataInventory._get_updated_metadata_df_for_csv_write(
        data_source_name="penguin_size",
        active_data_dict={
            "test_app_deploy_data/data/penguin_size/penguin_size.csv": INACTIVE,
            "test_app_deploy_data/data/penguin_size/penguin_size_2.csv": INACTIVE,
            new_upload_id: ACTIVE,
        },
    )
    expected_df = MOCK_METADATA.copy()
    # write the new row- we're missing values for notes and username for this
    new_row = {TABLE_NAME: "penguin_size", UPLOAD_ID: new_upload_id, ACTIVE: True}
    expected_df = expected_df.append(
        pd.DataFrame([new_row], columns=expected_df.columns)
    ).reset_index(drop=True)
    assert data_upload_metadata.equals(expected_df)
