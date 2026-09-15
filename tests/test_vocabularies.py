from typing import Any

import pytest
from check_schemas import (
    find_duplicate_concept_id_violations,
    find_unregistered_vocabulary_violations,
    find_unresolved_example_violations,
    find_unresolved_use_scheme_violations,
)


@pytest.mark.parametrize(
    ("all_schemas_by_name", "vocabularies_by_name", "expected"),
    [
        pytest.param(
            {
                "dummy": {
                    "properties": {
                        "x": {"useScheme": "https://mex.rki.de/item/missing"}
                    }
                }
            },
            {"theme": [{"identifier": "https://mex.rki.de/item/theme-1"}]},
            [
                (
                    "dummy: useScheme 'https://mex.rki.de/item/missing' has no "
                    "matching vocabulary"
                )
            ],
            id="use-scheme-has-no-vocabulary",
        ),
        pytest.param(
            {
                "dummy": {
                    "properties": {"x": {"useScheme": "https://mex.rki.de/item/theme"}}
                }
            },
            {"theme": [{"identifier": "https://mex.rki.de/item/theme-1"}]},
            [],
            id="use-scheme-matches-filename",
        ),
        pytest.param(
            {
                "dummy": {
                    "properties": {
                        "x": {"useScheme": "https://mex.rki.de/item/alt-name"}
                    }
                }
            },
            {
                "theme": [
                    {
                        "identifier": "https://mex.rki.de/item/theme-1",
                        "inScheme": "https://mex.rki.de/item/alt-name",
                    }
                ]
            },
            [],
            id="use-scheme-matches-in-scheme",
        ),
    ],
)
def test_unresolved_use_scheme_violations_are_detected(
    all_schemas_by_name: dict[str, dict[str, Any]],
    vocabularies_by_name: dict[str, list[dict[str, Any]]],
    expected: list[str],
) -> None:
    violations = find_unresolved_use_scheme_violations(
        all_schemas_by_name, vocabularies_by_name
    )
    assert violations == expected


@pytest.mark.parametrize(
    ("vocabulary_names", "concept_scheme_identifiers", "expected"),
    [
        pytest.param(
            {"made_up_vocab"},
            {"https://mex.rki.de/item/other"},
            [
                (
                    "made_up_vocab: identifier "
                    "'https://mex.rki.de/item/made-up-vocab' not found in "
                    "concept-schemes.json"
                )
            ],
            id="unregistered-vocabulary",
        ),
        pytest.param(
            {"theme"},
            {"https://mex.rki.de/item/theme"},
            [],
            id="registered-vocabulary",
        ),
    ],
)
def test_unregistered_vocabulary_violations_are_detected(
    vocabulary_names: set[str],
    concept_scheme_identifiers: set[str],
    expected: list[str],
) -> None:
    violations = find_unregistered_vocabulary_violations(
        vocabulary_names, concept_scheme_identifiers
    )
    assert violations == expected


@pytest.mark.parametrize(
    ("vocabularies_by_name", "expected"),
    [
        pytest.param(
            {"foo": [{"identifier": "a"}, {"identifier": "a"}]},
            ["foo: duplicate identifier 'a'"],
            id="duplicate-identifier",
        ),
        pytest.param(
            {"foo": [{"identifier": "a"}, {"identifier": "b"}]},
            [],
            id="unique-identifiers",
        ),
    ],
)
def test_duplicate_concept_id_violations_are_detected(
    vocabularies_by_name: dict[str, list[dict[str, Any]]], expected: list[str]
) -> None:
    violations = find_duplicate_concept_id_violations(vocabularies_by_name)
    assert violations == expected


@pytest.mark.parametrize(
    ("all_schemas_by_name", "vocabularies_by_name", "expected"),
    [
        pytest.param(
            {
                "dummy": {
                    "properties": {
                        "x": {
                            "useScheme": "https://mex.rki.de/item/theme",
                            "examples": ["https://mex.rki.de/item/theme-999"],
                        }
                    }
                }
            },
            {"theme": [{"identifier": "https://mex.rki.de/item/theme-1"}]},
            [
                (
                    "dummy: example 'https://mex.rki.de/item/theme-999' not found "
                    "in vocabulary 'theme'"
                )
            ],
            id="example-not-in-vocabulary",
        ),
        pytest.param(
            {
                "dummy": {
                    "properties": {
                        "x": {
                            "useScheme": "https://mex.rki.de/item/missing",
                            "examples": ["a"],
                        }
                    }
                }
            },
            {},
            [
                (
                    "dummy: useScheme 'https://mex.rki.de/item/missing' has no "
                    "matching vocabulary file"
                )
            ],
            id="use-scheme-has-no-vocabulary-file",
        ),
        pytest.param(
            {
                "dummy": {
                    "properties": {
                        "x": {
                            "useScheme": "https://mex.rki.de/item/theme",
                            "examples": ["https://mex.rki.de/item/theme-1"],
                        }
                    }
                }
            },
            {"theme": [{"identifier": "https://mex.rki.de/item/theme-1"}]},
            [],
            id="example-resolves",
        ),
        pytest.param(
            {
                "dummy": {
                    "properties": {"x": {"useScheme": "https://mex.rki.de/item/theme"}}
                }
            },
            {"theme": [{"identifier": "https://mex.rki.de/item/theme-1"}]},
            [],
            id="use-scheme-without-examples-is-ignored",
        ),
    ],
)
def test_unresolved_example_violations_are_detected(
    all_schemas_by_name: dict[str, dict[str, Any]],
    vocabularies_by_name: dict[str, list[dict[str, Any]]],
    expected: list[str],
) -> None:
    violations = find_unresolved_example_violations(
        all_schemas_by_name, vocabularies_by_name
    )
    assert violations == expected
