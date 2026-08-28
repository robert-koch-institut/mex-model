from typing import Any

import pytest
from check_schemas import (
    _all_entity_schemas_by_file_stem,
    _collect_violations,
    _load_extension_definition,
    find_id_path_violations,
    find_meta_schema_violations,
)

from mex.model import FIELD_JSON_BY_NAME


def test_collect_violations_finds_nothing_for_real_schemas() -> None:
    """Exercises the same aggregation used by the schema-checks pre-commit hook."""
    assert _collect_violations() == []


def test_schemas_are_valid_json_schema_documents() -> None:
    all_entities = _all_entity_schemas_by_file_stem()
    violations = [
        violation
        for name, schema in {**all_entities, **FIELD_JSON_BY_NAME}.items()
        for violation in find_meta_schema_violations(name, schema)
    ]
    violations += find_meta_schema_violations(
        "extension/definition", _load_extension_definition()
    )
    assert violations == []


@pytest.mark.parametrize(
    ("schema", "expected_message_contains"),
    [
        pytest.param(
            {"type": 123},
            "invalid JSON Schema document",
            id="invalid-type-keyword",
        ),
    ],
)
def test_meta_schema_violations_are_detected(
    schema: dict[str, Any], expected_message_contains: str
) -> None:
    violations = find_meta_schema_violations("dummy", schema)
    assert len(violations) == 1
    assert expected_message_contains in violations[0]


def test_meta_schema_violations_are_not_raised_for_valid_schema() -> None:
    assert find_meta_schema_violations("dummy", {"type": "string"}) == []


def test_schema_ids_match_their_file_paths() -> None:
    violations = []
    for name, schema in _all_entity_schemas_by_file_stem().items():
        violations += find_id_path_violations(name, "entities", schema)
    for name, schema in FIELD_JSON_BY_NAME.items():
        violations += find_id_path_violations(name, "fields", schema)
    violations += find_id_path_violations(
        "definition", "extension", _load_extension_definition()
    )
    assert violations == []


@pytest.mark.parametrize(
    ("normalized_name", "collection", "schema", "expected"),
    [
        pytest.param(
            "activity",
            "entities",
            {"$id": "https://mex.rki.de/mex/model/entities/wrong-name"},
            [
                (
                    "entities/activity: $id is "
                    "'https://mex.rki.de/mex/model/entities/wrong-name', "
                    "expected 'https://mex.rki.de/mex/model/entities/activity'"
                )
            ],
            id="mismatched-id",
        ),
        pytest.param(
            "activity",
            "entities",
            {
                "$id": "https://mex.rki.de/mex/model/entities/activity",
                "$$target": "/mex/model/entities/activity#/wrong",
            },
            [
                (
                    "entities/activity: $$target is "
                    "'/mex/model/entities/activity#/wrong', expected "
                    "'/mex/model/entities/activity#/identifier'"
                )
            ],
            id="mismatched-target",
        ),
        pytest.param(
            "activity",
            "entities",
            {
                "$id": "https://mex.rki.de/mex/model/entities/activity",
                "$$target": "/mex/model/entities/activity#/identifier",
            },
            [],
            id="matching-id-and-target",
        ),
    ],
)
def test_id_path_violations_are_detected(
    normalized_name: str,
    collection: str,
    schema: dict[str, Any],
    expected: list[str],
) -> None:
    assert find_id_path_violations(normalized_name, collection, schema) == expected
