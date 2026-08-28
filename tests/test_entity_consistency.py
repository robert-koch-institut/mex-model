from typing import Any

import pytest
from check_schemas import find_extracted_merged_parity_violations


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
