from collections.abc import Iterator
from typing import Any

import pytest
from check_schemas import (
    _all_entity_schemas_by_file_stem,
    _load_concept_scheme_identifiers,
    find_duplicate_concept_id_violations,
    find_unregistered_vocabulary_violations,
    find_unresolved_example_violations,
)

from mex.model import (
    EXTRACTED_MODEL_JSON_BY_NAME,
    MERGED_MODEL_JSON_BY_NAME,
    VOCABULARY_JSON_BY_NAME,
)


def _iter_use_schemes(node: object) -> Iterator[str]:
    """Yield all `useScheme` values found anywhere in the given json structure."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "useScheme":
                yield str(value)
            else:
                yield from _iter_use_schemes(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_use_schemes(item)


def test_use_schemes_resolve_to_vocabularies() -> None:
    use_schemes = {
        use_scheme
        for schema in (
            *EXTRACTED_MODEL_JSON_BY_NAME.values(),
            *MERGED_MODEL_JSON_BY_NAME.values(),
        )
        for use_scheme in _iter_use_schemes(schema)
    }
    known_schemes = {
        # note that `inScheme` and the filename do not always agree,
        # so a vocabulary is documented under either spelling
        f"https://mex.rki.de/item/{name.replace('_', '-')}"
        for name in VOCABULARY_JSON_BY_NAME
    } | {
        str(concept["inScheme"])
        for concepts in VOCABULARY_JSON_BY_NAME.values()
        for concept in concepts
        if "inScheme" in concept
    }
    # sanity check that we are actually comparing something
    assert "https://mex.rki.de/item/theme" in use_schemes
    # every scheme referenced by an entity must have a vocabulary
    assert sorted(use_schemes - known_schemes) == []


def test_vocabularies_are_registered_in_concept_schemes() -> None:
    violations = find_unregistered_vocabulary_violations(
        VOCABULARY_JSON_BY_NAME, _load_concept_scheme_identifiers()
    )
    assert violations == []


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


def test_vocabulary_identifiers_are_unique() -> None:
    violations = find_duplicate_concept_id_violations(VOCABULARY_JSON_BY_NAME)
    assert violations == []


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


def test_entity_examples_resolve_to_vocabulary_concepts() -> None:
    violations = find_unresolved_example_violations(
        _all_entity_schemas_by_file_stem(), VOCABULARY_JSON_BY_NAME
    )
    assert violations == []


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
