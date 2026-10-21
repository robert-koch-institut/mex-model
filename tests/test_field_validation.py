from typing import Any

import pytest
from check_schemas import (
    find_annotation_uri_violations,
    find_field_validation_violations,
    find_orphaned_field_violations,
    find_superseded_gate_violations,
)

GATED_PROPERTIES: dict[str, Any] = {
    "identifier": {"$ref": "/mex/model/fields/identifier"},
    "supersededBy": {"anyOf": [{"type": "string"}, {"type": "null"}]},
    "foo": {"type": "array", "default": []},
    "bar": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
}
GATE_IF: dict[str, Any] = {"properties": {"supersededBy": {"type": "null"}}}
GATE_THEN: dict[str, Any] = {
    "properties": {"foo": {"minItems": 1}, "bar": {"not": {"type": "null"}}},
    "required": ["bar", "foo"],
}
GATE_ELSE: dict[str, Any] = {
    "properties": {"foo": {"maxItems": 0}, "bar": {"type": "null"}}
}


def gated_schema(**gate: object) -> dict[str, Any]:
    return {
        "properties": GATED_PROPERTIES,
        "required": ["identifier"],
        "allOf": [{"if": GATE_IF, "then": GATE_THEN, "else": GATE_ELSE, **gate}],
    }


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
                "properties": {"foo": {"type": "array", "minItems": 1, "default": []}},
                "required": ["foo"],
            },
            ["dummy.foo: has minItems but also has a default"],
            id="required-array-with-default",
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
    ("schema", "expected"),
    [
        pytest.param(gated_schema(), [], id="valid-gate"),
        pytest.param(
            {**gated_schema(), "required": ["identifier", "foo"]},
            ["dummy: top-level required must only list identifier"],
            id="gated-field-in-top-level-required",
        ),
        pytest.param(
            {**gated_schema(), "allOf": []},
            ["dummy: missing supersededBy gate in allOf"],
            id="missing-gate",
        ),
        pytest.param(
            gated_schema(**{"if": {"required": ["supersededBy"]}}),
            ["dummy: missing supersededBy gate in allOf"],
            id="wrong-if-condition",
        ),
        pytest.param(
            gated_schema(then={**GATE_THEN, "required": ["foo"]}),
            ["dummy: gate then.required does not match then.properties"],
            id="then-required-out-of-sync",
        ),
        pytest.param(
            gated_schema(
                then={
                    "properties": {**GATE_THEN["properties"], "baz": {"minItems": 1}},
                    "required": ["bar", "baz", "foo"],
                }
            ),
            ["dummy: gate then.required lists unknown fields"],
            id="then-lists-unknown-field",
        ),
        pytest.param(
            gated_schema(**{"else": {"properties": {"foo": {"maxItems": 0}}}}),
            [
                (
                    "dummy: gate else.properties must cover every field "
                    "except identifier and supersededBy"
                )
            ],
            id="else-misses-field",
        ),
        pytest.param(
            gated_schema(**{"else": {"properties": {"foo": {"const": []}, "bar": {}}}}),
            [
                "dummy.bar: gate else must be {'type': 'null'}",
                "dummy.foo: gate else must be {'maxItems': 0}",
            ],
            id="else-with-wrong-constraints",
        ),
        pytest.param(
            gated_schema(
                then={
                    "properties": {"foo": {"minItems": 2}, "bar": {}},
                    "required": ["bar", "foo"],
                }
            ),
            [
                "dummy.bar: gate then must be {'not': {'type': 'null'}}",
                "dummy.foo: gate then must be {'minItems': 1}",
            ],
            id="then-with-wrong-constraints",
        ),
    ],
)
def test_superseded_gate_violations_are_detected(
    schema: dict[str, Any], expected: list[str]
) -> None:
    assert find_superseded_gate_violations("dummy", schema) == expected


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
            {"properties": {"foo": {"closeMatch": "https://example.com/a"}}},
            ["dummy.foo.closeMatch: 'https://example.com/a' is not an array"],
            id="string-instead-of-array",
        ),
        pytest.param(
            {"properties": {"foo": {"exactMatch": "not-a-uri"}}},
            [
                "dummy.foo.exactMatch: 'not-a-uri' is not an array",
                "dummy.foo.exactMatch: 'not-a-uri' is not a well-formed URI",
            ],
            id="malformed-string-instead-of-array",
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
