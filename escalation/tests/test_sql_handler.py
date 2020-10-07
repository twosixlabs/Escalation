# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import os

from flask import current_app
import pandas as pd
import pytest
from sqlalchemy import create_engine, MetaData

from database.sql_handler import SqlDataInventory, SqlHandler
from database.utils import sql_handler_filter_operation
from utility.constants import *
from tests.conftest import TESTING_DB_URI

PENGUIN_SIZE = "penguin_size"
PENGUIN_SIZE_SMALL = "penguin_size_small"

SEX = "sex"
ISLAND = "island"
BODY_MASS = "body_mass_g"
CULMEN_LENGTH = "culmen_length_mm"
CULMEN_DEPTH = "culmen_depth_mm"
FLIPPER_LENGTH = "flipper_length_mm"


@pytest.fixture()
def rebuild_test_database(test_app_client_sql_backed):
    # drop all tables associated with the testing app Sqlalchemy Base
    engine = create_engine(TESTING_DB_URI)
    current_app.engine = engine
    current_app.Base.metadata.drop_all(bind=engine)
    current_app.Base.metadata.create_all(bind=engine)

    test_app_data_path = os.path.join(TEST_APP_DEPLOY_DATA, DATA)
    data_sources = os.listdir(test_app_data_path)
    for data_source in data_sources:
        if data_source == DATA_UPLOAD_METADATA or data_source.startswith("."):
            continue
        data_inventory = SqlDataInventory(
            data_sources={MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: data_source}}
        )
        data_source_path = os.path.join(test_app_data_path, data_source)
        files = os.listdir(data_source_path)
        for file in files:
            df = pd.read_csv(os.path.join(data_source_path, file), sep=",", comment="#")
            data_inventory.write_data_upload_to_backend(
                df, username="test_fixture", notes="test case upload"
            )
    return True


@pytest.fixture()
def get_sql_handler_fixture(rebuild_test_database):
    data_sources = {
        MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "penguin_size"},
        ADDITIONAL_DATA_SOURCES: [
            {
                DATA_SOURCE_TYPE: "mean_penguin_stat",
                JOIN_KEYS: [
                    ["penguin_size:study_name", "mean_penguin_stat:study_name"],
                    ["penguin_size:sex", "mean_penguin_stat:sex"],
                    ["penguin_size:species", "mean_penguin_stat:species"],
                ],
            }
        ],
    }
    return SqlHandler(data_sources)


@pytest.fixture()
def get_sql_handler_fixture_small(rebuild_test_database):
    return SqlHandler({MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "penguin_size_small"}})


def test_sql_handler_init(get_sql_handler_fixture):
    data_sources = get_sql_handler_fixture.flat_data_sources
    assert "penguin_size" == data_sources[0][DATA_SOURCE_TYPE]
    assert "mean_penguin_stat" == data_sources[1][DATA_SOURCE_TYPE]


def test_get_column_data_no_filter(get_sql_handler_fixture_small):
    # also test apply filters to data
    data_dict = [
        "penguin_size_small:body_mass_g",
        "penguin_size_small:flipper_length_mm",
    ]
    test_dict = get_sql_handler_fixture_small.get_column_data(data_dict)
    assert (test_dict["penguin_size_small:body_mass_g"] == [3750, 3800, 3250]).all()
    assert (test_dict["penguin_size_small:flipper_length_mm"] == [181, 186, 195]).all()


def test_get_column_data_filter(get_sql_handler_fixture_small):
    # also test apply filters to data
    data_dict = [
        "penguin_size_small:body_mass_g",
        "penguin_size_small:flipper_length_mm",
    ]
    test_dict = get_sql_handler_fixture_small.get_column_data(
        data_dict,
        [{"type": "filter", "column": "penguin_size_small:sex", "selected": ["MALE"]}],
    )
    assert (test_dict["penguin_size_small:body_mass_g"] == [3750]).all()
    assert (test_dict["penguin_size_small:flipper_length_mm"] == [181]).all()


def test_get_column_data_numerical_filter(get_sql_handler_fixture_small):
    data_dict = [
        "penguin_size_small:body_mass_g",
        "penguin_size_small:flipper_length_mm",
    ]
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


def test_get_column_unique_entries(get_sql_handler_fixture):
    unique_entries = get_sql_handler_fixture.get_column_unique_entries(
        ["penguin_size:sex", "penguin_size:island",]
    )
    assert set(unique_entries["penguin_size:sex"]) == {"MALE", "FEMALE", "."}
    assert set(unique_entries["penguin_size:island"]) == {
        "Dream",
        "Torgersen",
        "Biscoe",
    }


def test_build_combined_data_table(get_sql_handler_fixture):
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
    rows = get_sql_handler_fixture.get_column_data([f"{PENGUIN_SIZE}:{CULMEN_DEPTH}"])[
        f"{PENGUIN_SIZE}:{CULMEN_DEPTH}"
    ]
    num_rows_in_combined_table = len(rows)
    assert num_rows_in_inner_table == num_rows_in_combined_table


def test_build_combined_data_table_with_filtered_data_source(get_sql_handler_fixture):
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
        PENGUIN_SIZE, {1: "ACTIVE", 2: "INACTIVE"}
    )
    num_rows_in_combined_table = len(
        get_sql_handler_fixture.get_column_data(
            [f"{PENGUIN_SIZE}:{ISLAND}"],
            [{"type": FILTER, "column": f"{PENGUIN_SIZE}:upload_id", "selected": [1],}],
        )[f"{PENGUIN_SIZE}:{ISLAND}"]
    )
    assert num_rows_in_inner_table == num_rows_in_combined_table


def test_get_available_data_sources(rebuild_test_database):
    file_names = SqlDataInventory.get_available_data_sources()
    assert "penguin_size_small" in file_names
    assert "penguin_size" in file_names
    assert "mean_penguin_stat" in file_names
    assert len(file_names) == 3


def test_get_schema_for_data_source(get_sql_handler_fixture):
    column_names = get_sql_handler_fixture.get_schema_for_data_source()
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


def test_write_data_upload_to_backend():
    assert False


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
