from utility.build_schema import build_graphic_schema_with_plotly
import jsonschema


def test_if_schema_is_valid_schema():
    # The input needs to be nonempty lists of strings for it to be a valid schema
    schema = build_graphic_schema_with_plotly(
        ["words"], ["words"], ["words"], ["words"], ["a", "b"]
    )
    jsonschema.Draft7Validator.check_schema(schema)
    assert True
