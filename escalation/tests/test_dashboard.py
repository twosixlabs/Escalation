from werkzeug.datastructures import ImmutableMultiDict

from views.dashboard import add_form_to_addendum_dict


def test_add_form_to_addendum_dict():
    addendum_dict = {
        "graphic_0": {
            "filter_0": ["MALE"],
            "filter_1": ["Torgersen", "Dream"],
            "numerical_filter_0_max_value": ["4"],
            "numerical_filter_0_min_value": [""],
        }
    }

    form = ImmutableMultiDict(
        [
            ("graphic_name", "graphic_0"),
            ("filter_0", "MALE"),
            ("filter_1", "Torgersen"),
            ("filter_1", "Dream"),
            ("numerical_filter_0_max_value", "4"),
            ("numerical_filter_0_min_value", ""),
        ]
    )
    new_addendum_dict = {}
    add_form_to_addendum_dict(form, new_addendum_dict)
    assert new_addendum_dict == addendum_dict
