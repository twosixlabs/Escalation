from utility.constants import (
    AVAILABLE_PAGES,
    WEBPAGE_LABEL,
    URL_ENDPOINT,
    GRAPHIC_CONFIG_FILES,
    GRAPHIC_PATH,
)
from wizard_ui.wizard_utils import invert_dict_lists, get_layout_for_dashboard


def test_invert_dict_lists():
    test_dict = {"a": [1], "b": [2, 3]}
    expected_dict = {1: "a", 2: "b", 3: "b"}
    inverted_dict = invert_dict_lists(test_dict)
    assert inverted_dict == expected_dict


def test_get_layout_for_dashboard(main_json_fixture):
    # Need to set up file system
    new_dict = get_layout_for_dashboard(main_json_fixture[AVAILABLE_PAGES])

    ground_truth = (
        [
            {
                WEBPAGE_LABEL: "PENGUINS!",
                URL_ENDPOINT: "penguin",
                GRAPHIC_CONFIG_FILES: [
                    {GRAPHIC_PATH: "big_penguins.json"},
                    "hist_penguins.json",
                ],
            },
            {
                WEBPAGE_LABEL: "Radio Penguins",
                URL_ENDPOINT: "radio_penguins",
                GRAPHIC_CONFIG_FILES: ["radio_penguins.json"],
            },
        ],
    )
    assert False
