from typing import Any

import pytest
from check_schemas import (
    find_extracted_merged_parity_violations,
    find_field_identity_violations,
)


@pytest.mark.parametrize(
    ("extracted_by_name", "merged_by_name", "expected"),
    [
        pytest.param(
            {"foo": {"properties": {"a": {}, "extra": {}}}},
            {"foo": {"properties": {"a": {}}}},
            ["foo: fields only in extracted schema: ['extra']"],
            id="extra-field-in-extracted",
        ),
        pytest.param(
            {"foo": {"properties": {"a": {}}}},
            {"foo": {"properties": {"a": {}, "extra": {}}}},
            ["foo: fields only in merged schema: ['extra']"],
            id="extra-field-in-merged",
        ),
        pytest.param(
            {"foo": {"properties": {}}},
            {},
            ["foo: no merged- schema found"],
            id="missing-merged-schema",
        ),
        pytest.param(
            {},
            {"foo": {"properties": {}}},
            ["foo: no extracted- schema found"],
            id="missing-extracted-schema",
        ),
        pytest.param(
            {
                "foo": {
                    "properties": {
                        "a": {},
                        "hadPrimarySource": {},
                        "identifierInPrimarySource": {},
                        "stableTargetId": {},
                    }
                }
            },
            {"foo": {"properties": {"a": {}, "supersededBy": {}}}},
            [],
            id="excluded-provenance-fields-do-not-trigger-false-positive",
        ),
    ],
)
def test_extracted_merged_parity_violations_are_detected(
    extracted_by_name: dict[str, dict[str, Any]],
    merged_by_name: dict[str, dict[str, Any]],
    expected: list[str],
) -> None:
    violations = find_extracted_merged_parity_violations(
        extracted_by_name, merged_by_name
    )
    assert violations == expected


@pytest.mark.parametrize(
    ("all_schemas_by_name", "expected"),
    [
        pytest.param(
            {
                "a": {"properties": {"foo": {"type": "string"}}},
                "b": {"properties": {"foo": {"type": "string"}}},
            },
            [],
            id="identical-shape",
        ),
        pytest.param(
            {
                "a": {"properties": {"foo": {"type": "string"}}},
                "b": {"properties": {"foo": {"type": "integer"}}},
                "c": {"properties": {"foo": {"type": "string"}}},
            },
            ["foo: ['b'] declared differently than ['a', 'c']"],
            id="minority-shape-flagged",
        ),
        pytest.param(
            {
                "a": {
                    "properties": {
                        "foo": {
                            "type": "string",
                            "closeMatch": ["https://example.com/a"],
                            "$comment": "note a",
                            "description": "desc a",
                            "examples": ["x"],
                        }
                    }
                },
                "b": {
                    "properties": {
                        "foo": {
                            "type": "string",
                            "closeMatch": ["https://example.com/b"],
                            "$comment": "note b",
                            "description": "desc b",
                            "examples": ["y"],
                        }
                    }
                },
            },
            [],
            id="annotation-and-example-drift-is-ignored",
        ),
        pytest.param(
            {
                "a": {
                    "properties": {
                        "foo": {
                            "type": "array",
                            "minItems": 1,
                            "items": {"type": "string"},
                        }
                    }
                },
                "b": {
                    "properties": {
                        "foo": {
                            "type": "array",
                            "default": [],
                            "items": {"type": "string"},
                        }
                    }
                },
            },
            [],
            id="required-ness-array-drift-is-ignored",
        ),
        pytest.param(
            {
                "a": {
                    "properties": {
                        "foo": {"anyOf": [{"type": "string"}, {"type": "null"}]}
                    }
                },
                "b": {"properties": {"foo": {"anyOf": [{"type": "string"}]}}},
            },
            [],
            id="required-ness-scalar-null-branch-drift-is-ignored",
        ),
        pytest.param(
            {
                "a": {"properties": {"stableTargetId": {"$ref": "a"}}},
                "b": {"properties": {"stableTargetId": {"$ref": "b"}}},
            },
            [],
            id="excluded-provenance-field-is-ignored",
        ),
    ],
)
def test_field_identity_violations_are_detected(
    all_schemas_by_name: dict[str, dict[str, Any]], expected: list[str]
) -> None:
    violations = find_field_identity_violations(all_schemas_by_name)
    assert violations == expected
