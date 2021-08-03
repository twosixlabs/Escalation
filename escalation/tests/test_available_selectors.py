from utility.available_selectors import get_key_for_form, make_filter_dict
from utility.constants import GROUPBY, NUMERICAL_FILTER, FILTER, SHOW_ALL_ROW


def test_get_key_for_form():
    assert "filter_1" == get_key_for_form(FILTER, 1)
    assert "numerical_filter_4" == get_key_for_form(NUMERICAL_FILTER, 4)
    assert "groupby" == get_key_for_form(GROUPBY, "")


def test_make_filter_dict_filters():
    selector_dict = {
        "filter": [
            {
                "column": "penguin_size:sex",
                "multiple": False,
                "active_selector": ["Show All Rows"],
            },
            {
                "column": "penguin_size:island",
                "multiple": True,
                "default_selected": ["Dream"],
                "active_selector": ["Dream"],
            },
        ],
        "numerical_filter": [
            {
                "column": "penguin_size:culmen_length_mm",
                "type": "number",
                "active_selector": {"max": {"value": ""}, "min": {"value": ""}},
            }
        ],
    }

    penguin_sexes = ([SHOW_ALL_ROW, "XX", "XY"],)  # penguin sexes column entries
    penguin_islands = [SHOW_ALL_ROW, "Dream"]  # penguin islands column entries

    entries_for_columns = [penguin_sexes, penguin_islands]
    created_filter_dicts = []
    for index, selector_items in enumerate(selector_dict[FILTER]):
        created_filter_dicts.append(
            make_filter_dict(
                FILTER,
                selector_items,
                index,
                selector_entries=entries_for_columns[index],
            )
        )

    expected_filter_dict_sexes = {
        "type": "",
        "select_html_file": "selector.html",
        "name": "filter_0",
        "text": "Filter by penguin_size:sex",
        "active_selector": ["Show All Rows"],
        "multiple": False,
        "entries": penguin_sexes,
    }
    assert created_filter_dicts[0] == expected_filter_dict_sexes

    expected_filter_dict_islands = {
        "type": "",
        "select_html_file": "selector.html",
        "name": "filter_1",
        "text": "Filter by penguin_size:island",
        "active_selector": ["Dream"],
        "multiple": True,
        "entries": penguin_islands,
    }
    assert created_filter_dicts[1] == expected_filter_dict_islands

    created_filter_dict = make_filter_dict(
        NUMERICAL_FILTER,
        selector_dict[NUMERICAL_FILTER][0],  # get the entry from the list of filters
        index=0,
    )

    expected_numerical_filter_dict = {
        "type": "number",
        "select_html_file": "numerical_filter.html",
        "name": "numerical_filter_0",
        "text": "Filter by penguin_size:culmen_length_mm",
        "active_selector": {"max": {"value": ""}, "min": {"value": ""}},
        "multiple": False,
        "entries": None,
    }
    assert expected_numerical_filter_dict == created_filter_dict
