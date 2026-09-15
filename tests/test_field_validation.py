from typing import Any

import pytest
from check_schemas import (
    find_annotation_uri_violations,
    find_field_validation_violations,
    find_orphaned_field_violations,
)


@pytest.mark.parametrize(
    ("schema", "expected"),
    [
        pytest.param(
            {"properties": {"foo": {"type": "array", "minItems": 1}}, "required": []},
            ["dummy.foo: has minItems but is not in required"],
            id="required-array-not-in-required",
        ),
        pytest.param(
            {
                "properties": {"foo": {"type": "array", "default": []}},
                "required": ["foo"],
            },
            ["dummy.foo: is required but has no minItems"],
            id="array-in-required-without-min-items",
        ),
        pytest.param(
            {"properties": {"foo": {"type": "array"}}, "required": []},
            ["dummy.foo: optional array is missing a default"],
            id="optional-array-missing-default",
        ),
        pytest.param(
            {"properties": {"foo": {"type": "array", "default": []}}, "required": []},
            [],
            id="valid-optional-array",
        ),
        pytest.param(
            {
                "properties": {"foo": {"type": "array", "minItems": 1}},
                "required": ["foo"],
            },
            [],
            id="valid-required-array",
        ),
        pytest.param(
            {
                "properties": {"foo": {"anyOf": [{"type": "string"}], "default": None}},
                "required": [],
            },
            ["dummy.foo: optional scalar is missing anyOf null"],
            id="optional-scalar-missing-any-of-null",
        ),
        pytest.param(
            {
                "properties": {
                    "foo": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": "x",
                    }
                },
                "required": [],
            },
            ["dummy.foo: optional scalar default is not null"],
            id="optional-scalar-default-not-null",
        ),
        pytest.param(
            {
                "properties": {
                    "foo": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                    }
                },
                "required": [],
            },
            [],
            id="valid-optional-scalar",
        ),
        pytest.param(
            {"properties": {}, "required": ["foo"]},
            ["dummy.foo: listed in required but missing from properties"],
            id="required-references-missing-property",
        ),
        pytest.param(
            {"properties": {"foo": {"type": "string"}}, "required": ["foo"]},
            [],
            id="valid-required-scalar",
        ),
    ],
)
def test_field_validation_violations_are_detected(
    schema: dict[str, Any], expected: list[str]
) -> None:
    assert find_field_validation_violations("dummy", schema) == expected


@pytest.mark.parametrize(
    ("field_names", "schemas", "expected"),
    [
        pytest.param(
            {"orphan"},
            {"dummy": {"properties": {}}},
            ["orphan: not referenced by any entity schema"],
            id="orphaned-field",
        ),
        pytest.param(
            {"identifier"},
            {"dummy": {"properties": {"id": {"$ref": "/mex/model/fields/identifier"}}}},
            [],
            id="referenced-field",
        ),
        pytest.param(
            {"identifier"},
            {
                "dummy": {
                    "properties": {
                        "id": {"anyOf": [{"$ref": "/mex/model/fields/identifier"}]}
                    }
                }
            },
            [],
            id="referenced-field-nested-in-list",
        ),
    ],
)
def test_orphaned_field_violations_are_detected(
    field_names: set[str], schemas: dict[str, dict[str, Any]], expected: list[str]
) -> None:
    assert find_orphaned_field_violations(field_names, schemas) == expected


@pytest.mark.parametrize(
    ("schema", "expected"),
    [
        pytest.param(
            {"properties": {"foo": {"closeMatch": ["not-a-uri"]}}},
            ["dummy.foo.closeMatch: 'not-a-uri' is not a well-formed URI"],
            id="malformed-uri",
        ),
        pytest.param(
            {
                "properties": {
                    "foo": {
                        "closeMatch": [
                            "https://example.com/a",
                            "https://example.com/a",
                        ]
                    }
                }
            },
            ["dummy.foo.closeMatch: 'https://example.com/a' is duplicated"],
            id="duplicated-uri",
        ),
        pytest.param(
            {"properties": {"foo": {"closeMatch": ["https://example.com/a"]}}},
            [],
            id="valid-uri",
        ),
    ],
)
def test_annotation_uri_violations_are_detected(
    schema: dict[str, Any], expected: list[str]
) -> None:
    assert find_annotation_uri_violations("dummy", schema) == expected
