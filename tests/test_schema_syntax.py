import re
from collections.abc import Callable
from types import ModuleType
from typing import Any

import check_entities
import check_vocabularies
import pytest
from check_entities import (
    find_id_path_violations,
    find_meta_schema_violations,
)

CHECK_FUNCTION_NAME_PATTERN = re.compile(r"^find_.*_(violations|warnings)$")
CHECK_MODULES = [
    pytest.param(check_entities, id="check_entities"),
    pytest.param(check_vocabularies, id="check_vocabularies"),
]


@pytest.mark.parametrize("module", CHECK_MODULES)
def test_collect_violations_calls_every_check_function(
    module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every check function must be wired into its collector.

    `find_*_violations` functions must be called from `_collect_violations` and
    `find_*_warnings` functions from `_collect_warnings`. Check functions are discovered by name convention rather than a hand-kept
    list, so adding a new check and forgetting to call it from
    `_collect_violations` fails here instead of silently never running against
    real data.
    """
    check_names = [
        name
        for name, value in vars(module).items()
        if CHECK_FUNCTION_NAME_PATTERN.match(name) and callable(value)
    ]
    assert check_names  # sanity check the discovery mechanism finds something

    call_counts = dict.fromkeys(check_names, 0)
    for name in check_names:
        original: Callable[..., list[str]] = getattr(module, name)

        def spy(
            *args: object,
            _original: Callable[..., list[str]] = original,
            _name: str = name,
            **kwargs: object,
        ) -> list[str]:
            call_counts[_name] += 1
            return _original(*args, **kwargs)

        monkeypatch.setattr(module, name, spy)

    module._collect_violations()
    if hasattr(module, "_collect_warnings"):
        module._collect_warnings()

    uncalled = [name for name, count in call_counts.items() if count == 0]
    assert uncalled == []


@pytest.mark.parametrize("module", CHECK_MODULES)
def test_collect_violations_finds_nothing_for_real_data(module: ModuleType) -> None:
    """Exercises the same aggregation used by the pre-commit hooks."""
    assert module._collect_violations() == []


def test_collect_warnings_reports_shared_exact_matches_for_real_data() -> None:
    """Warnings are advisory: they are collected but never count as violations."""
    warnings = check_vocabularies._collect_warnings()
    assert all(" is shared by " in warning for warning in warnings)


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
