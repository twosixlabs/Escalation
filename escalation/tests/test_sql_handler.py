# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import pandas as pd
import pytest
import datetime
from sqlalchemy.types import Integer, Text, Float, DateTime, ARRAY, Boolean

from database.sql_handler import SqlDataInventory, SqlHandler
from utility.constants import *
from test_app_deploy_data.models import PenguinSize, DataUploadMetadata

PENGUIN_SIZE = "penguin_size"
PENGUIN_SIZE_SMALL = "penguin_size_small"

SEX = "sex"
ISLAND = "island"
BODY_MASS = "body_mass_g"
CULMEN_LENGTH = "culmen_length_mm"
CULMEN_DEPTH = "culmen_depth_mm"
FLIPPER_LENGTH = "flipper_length_mm"


@pytest.fixture()
def get_sql_handler_fixture_lter_table(rebuild_test_database):
    data_sources = {
        MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "penguin_lter_small"},
    }
    return SqlHandler(data_sources)


@pytest.fixture()
def get_sql_handler_fixture_small(rebuild_test_database):
    return SqlHandler({MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "penguin_size_small"}})


@pytest.fixture()
def get_sql_handler_fixture_temperature(rebuild_test_database):
    return SqlHandler({MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "temperature"}})


def test_sql_handler_init(sql_handler_fixture):
    data_sources = sql_handler_fixture.flat_data_sources
    assert "penguin_size" == data_sources[0][DATA_SOURCE_TYPE]
    assert "mean_penguin_stat" == data_sources[1][DATA_SOURCE_TYPE]


def test_get_column_data_no_filter(get_sql_handler_fixture_small):
    # also test apply filters to data
    data_dict = {
        "penguin_size_small:body_mass_g",
        "penguin_size_small:flipper_length_mm",
    }
    test_dict = get_sql_handler_fixture_small.get_column_data(data_dict)
    assert (test_dict["penguin_size_small:body_mass_g"] == [3750, 3800, 3250]).all()
    assert (test_dict["penguin_size_small:flipper_length_mm"] == [181, 186, 195]).all()


def test_get_column_data_filter(get_sql_handler_fixture_small):
    # also test apply filters to data
    data_dict = {
        "penguin_size_small:body_mass_g",
        "penguin_size_small:flipper_length_mm",
    }
    test_dict = get_sql_handler_fixture_small.get_column_data(
        data_dict,
        [{"type": "filter", "column": "penguin_size_small:sex", "selected": ["MALE"]}],
    )
    assert (test_dict["penguin_size_small:body_mass_g"] == [3750]).all()
    assert (test_dict["penguin_size_small:flipper_length_mm"] == [181]).all()


def test_get_column_data_numerical_filter(get_sql_handler_fixture_small):
    data_dict = {
        "penguin_size_small:body_mass_g",
        "penguin_size_small:flipper_length_mm",
    }
    test_dict = get_sql_handler_fixture_small.get_column_data(
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

    assert list(test_dict["penguin_size_small:body_mass_g"]) == [3750, 3800]
    assert list(test_dict["penguin_size_small:flipper_length_mm"]) == [181, 186]


def test_get_column_data_numerical_filter_datetime(get_sql_handler_fixture_temperature):
    data_dict = {
        "temperature:Date",
        "temperature:Temp",
    }
    test_dict = get_sql_handler_fixture_temperature.get_column_data(
        data_dict,
        [
            {
                "type": "numerical_filter",
                "column": "temperature:Date",
                "operation": "<=",
                "value": datetime.datetime(1981, 1, 2),
            }
        ],
    )

    assert list(test_dict["temperature:Date"]) == [
        datetime.datetime(1981, 1, 1),
        datetime.datetime(1981, 1, 2),
    ]


def test_get_column_unique_entries(sql_handler_fixture):
    unique_entries = sql_handler_fixture.get_column_unique_entries(
        ["penguin_size:sex", "penguin_size:island",]
    )
    assert set(unique_entries["penguin_size:sex"]) == {"MALE", "FEMALE", "."}
    assert set(unique_entries["penguin_size:island"]) == {
        "Dream",
        "Torgersen",
        "Biscoe",
    }


def test_build_combined_data_table(sql_handler_fixture):
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
    rows = sql_handler_fixture.get_column_data({f"{PENGUIN_SIZE}:{CULMEN_DEPTH}"})[
        f"{PENGUIN_SIZE}:{CULMEN_DEPTH}"
    ]
    num_rows_in_combined_table = len(rows)
    assert num_rows_in_inner_table == num_rows_in_combined_table


def test_build_combined_data_table_with_filtered_data_source(sql_handler_fixture):
    # only the one included penguin size is loaded, not the second
    penguin_size = pd.read_csv(
        "test_app_deploy_data/data/penguin_size/penguin_size.csv"
    )
    penguin_mean = pd.read_csv(
        "test_app_deploy_data/data/mean_penguin_stat/mean_penguin_stat.csv"
    )
    inner_join_table = pd.merge(
        penguin_size, penguin_mean, how="inner", on=["study_name", "sex", "species"]
    )
    num_rows_in_inner_table = inner_join_table.shape[0]
    SqlDataInventory.update_data_upload_metadata_active(
        PENGUIN_SIZE, {"id_1": "ACTIVE", "id_2": "INACTIVE"}
    )
    num_rows_in_combined_table = len(
        sql_handler_fixture.get_column_data(
            {f"{PENGUIN_SIZE}:{ISLAND}"},
            [{"type": FILTER, "column": f"{PENGUIN_SIZE}:upload_id", "selected": [1],}],
        )[f"{PENGUIN_SIZE}:{ISLAND}"]
    )
    assert num_rows_in_inner_table == num_rows_in_combined_table


def test_get_available_data_sources(rebuild_test_database):
    file_names = SqlDataInventory.get_available_data_sources()
    assert "penguin_size_small" in file_names
    assert "penguin_size" in file_names
    assert "mean_penguin_stat" in file_names
    assert "penguin_lter_small" in file_names
    assert "temperature" in file_names
    assert len(file_names) == 7


def get_column_names_for_data_source(get_sql_handler_fixture):
    column_names = get_sql_handler_fixture.get_column_names_for_data_source()
    expected_column_names = {
        "mean_penguin_stat:body_mass",
        "mean_penguin_stat:culmen_depth",
        "mean_penguin_stat:culmen_length",
        "mean_penguin_stat:delta_13_c",
        "mean_penguin_stat:delta_15_n",
        "mean_penguin_stat:flipper_length",
        "mean_penguin_stat:row_index",
        "mean_penguin_stat:sex",
        "mean_penguin_stat:species",
        "mean_penguin_stat:study_name",
        "mean_penguin_stat:upload_id",
        "penguin_size:body_mass_g",
        "penguin_size:culmen_depth_mm",
        "penguin_size:culmen_length_mm",
        "penguin_size:flipper_length_mm",
        "penguin_size:island",
        "penguin_size:region",
        "penguin_size:row_index",
        "penguin_size:sex",
        "penguin_size:species",
        "penguin_size:study_name",
        "penguin_size:upload_id",
    }

    assert set(column_names) == expected_column_names


def test_get_schema_for_data_source(sql_handler_fixture):
    column_types_dict = sql_handler_fixture.get_schema_for_data_source()
    expected_column_types = {
        "mean_penguin_stat:body_mass": Float,
        "mean_penguin_stat:culmen_depth": Float,
        "mean_penguin_stat:culmen_length": Float,
        "mean_penguin_stat:delta_13_c": Float,
        "mean_penguin_stat:delta_15_n": Float,
        "mean_penguin_stat:flipper_length": Float,
        "mean_penguin_stat:row_index": Integer,
        "mean_penguin_stat:sex": Text,
        "mean_penguin_stat:species": Text,
        "mean_penguin_stat:study_name": Text,
        "mean_penguin_stat:upload_id": Integer,
        "penguin_size:body_mass_g": Integer,
        "penguin_size:culmen_depth_mm": Float,
        "penguin_size:culmen_length_mm": Float,
        "penguin_size:flipper_length_mm": Integer,
        "penguin_size:island": Text,
        "penguin_size:region": Text,
        "penguin_size:row_index": Integer,
        "penguin_size:sex": Text,
        "penguin_size:species": Text,
        "penguin_size:study_name": Text,
        "penguin_size:upload_id": Integer,
    }
    for k, v in expected_column_types.items():
        print(v)
        assert isinstance(column_types_dict[k], v), k


def test_get_schema_for_lter_data_source(get_sql_handler_fixture_lter_table):
    column_types_dict = get_sql_handler_fixture_lter_table.get_schema_for_data_source()
    expected_column_types = {
        "penguin_lter_small:date_egg": DateTime,
        "penguin_lter_small:island": Text,
        "penguin_lter_small:study_name": Text,
        "penguin_lter_small:region_culmen_list": ARRAY,
        "penguin_lter_small:clutch_completion": Boolean,
    }
    for k, v in expected_column_types.items():
        assert isinstance(column_types_dict[k], v)


def test_write_data_upload_to_backend(
    rebuild_test_database,
    penguin_size_csv_file,
    sql_data_inventory_fixture,
    test_app_client_sql_backed_development_env,
):
    penguin_size_df = pd.read_csv(penguin_size_csv_file)
    session = test_app_client_sql_backed_development_env.db_session
    db_response = session.query(PenguinSize.upload_id).distinct()
    upload_ids_in_db = sorted([x.upload_id for x in db_response])
    expected_upload_ids = [1, 2]
    # check that the state of the db is as expected after setup
    assert upload_ids_in_db == expected_upload_ids

    # write the upload and look for a new upload id
    ignored_columns = sql_data_inventory_fixture.write_data_upload_to_backend(
        penguin_size_df, "test_user", "test_write_data_upload_to_backend_notes"
    )
    # check that no columns in the dataset were omitted from the db table write
    assert ignored_columns == set()
    db_response = session.query(PenguinSize.upload_id).distinct()
    upload_ids_in_db = sorted([x.upload_id for x in db_response])
    expected_upload_ids = [1, 2, 3]
    assert upload_ids_in_db == expected_upload_ids

    # check that extra columns in the csv not defined in table are ignored
    penguin_size_df["column_in_upload_not_db_schema"] = -99
    # write the upload and look for a new upload id
    ignored_columns = sql_data_inventory_fixture.write_data_upload_to_backend(
        penguin_size_df, "test_user", "test_write_data_upload_to_backend_notes"
    )
    assert ignored_columns == {"column_in_upload_not_db_schema"}

    # check that the metadata table has been updated
    db_response = (
        session.query(DataUploadMetadata.upload_id)
        .filter(DataUploadMetadata.table_name == "penguin_size")
        .distinct()
    )
    upload_ids_in_db = sorted([x.upload_id for x in db_response])
    expected_upload_ids = [1, 2, 3, 4]
    assert upload_ids_in_db == expected_upload_ids


def test_get_table_data(get_sql_handler_fixture_small):
    result = get_sql_handler_fixture_small.get_table_data()

    penguin_small = pd.read_csv(
        "test_app_deploy_data/data/penguin_size_small/penguin_size_small.csv"
    )
    penguin_small["upload_id"] = 1
    penguin_small["row_index"] = [0, 1, 2]
    assert all(
        result.sort_index().sort_index(axis=1)
        == penguin_small.sort_index().sort_index(axis=1)
    )
