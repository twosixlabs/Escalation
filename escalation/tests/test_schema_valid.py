import jsonschema


def test_if_schema_is_valid_schema():
    # The input needs to be nonempty lists of strings for it to be a valid schema
    schema = {}
    jsonschema.Draft7Validator.check_schema(schema)
    assert False
