import json
from importlib.resources import files
from typing import Any

import pytest
from check_vocabularies import (
    build_validators,
    find_concept_annotation_violations,
    find_concept_schema_violations,
    find_concept_scheme_schema_violations,
    find_duplicate_concept_id_violations,
    find_duplicate_concept_scheme_violations,
    find_duplicate_pref_label_violations,
    find_scheme_membership_violations,
    find_shared_exact_match_warnings,
    find_unbacked_concept_scheme_violations,
    find_unregistered_vocabulary_violations,
    find_unresolved_broader_violations,
    find_unresolved_example_violations,
    find_unresolved_use_scheme_violations,
)
from jsonschema import Draft202012Validator

THEME = "https://mex.rki.de/item/theme"
LABEL = {"de": "Thema", "en": "Topic"}


def _concept(number: int, **fields: object) -> dict[str, Any]:
    """Return a minimal valid theme concept, updated with the given fields."""
    return {
        "identifier": f"{THEME}-{number}",
        "inScheme": THEME,
        "prefLabel": {"de": f"Thema {number}", "en": f"Topic {number}"},
        **fields,
    }


@pytest.fixture(scope="module")
def validators() -> tuple[Draft202012Validator, Draft202012Validator]:
    """Build the concept and concept scheme validators from the real schemas."""
    entities = files("mex.model.entities")
    return build_validators(
        json.loads(entities.joinpath("concept.json").read_text("utf-8")),
        json.loads(entities.joinpath("concept-scheme.json").read_text("utf-8")),
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
    ("vocabularies_by_name", "expected"),
    [
        pytest.param(
            {"foo": [{"identifier": "a", "exactMatch": "https://example.com/a"}]},
            ["foo.a.exactMatch: 'https://example.com/a' is not an array"],
            id="string-instead-of-array",
        ),
        pytest.param(
            {"foo": [{"identifier": "a", "closeMatch": ["not-a-uri"]}]},
            ["foo.a.closeMatch: 'not-a-uri' is not a well-formed URI"],
            id="malformed-uri",
        ),
        pytest.param(
            {
                "foo": [
                    {"identifier": "a", "exactMatch": ["https://example.com/a"]},
                    {"identifier": "b"},
                ]
            },
            [],
            id="valid-array-or-absent",
        ),
    ],
)
def test_concept_annotation_violations_are_detected(
    vocabularies_by_name: dict[str, list[dict[str, Any]]], expected: list[str]
) -> None:
    violations = find_concept_annotation_violations(vocabularies_by_name)
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


@pytest.mark.parametrize(
    ("concept", "expected"),
    [
        pytest.param(
            _concept(
                1,
                altLabel=[{"en": "Subject"}],
                broader=[f"{THEME}-2"],
                definition=[{"en": "A topic."}],
                exactMatch=["https://example.com/topic"],
                notation="1.0",
                note={"de": "Hinweis", "en": "Note"},
            ),
            [],
            id="valid-concept-with-all-fields",
        ),
        pytest.param(
            _concept(1, prefLabel=[LABEL]),
            [
                (
                    "theme.https://mex.rki.de/item/theme-1.prefLabel: "
                    "[{'de': 'Thema', 'en': 'Topic'}] is not of type 'object'"
                )
            ],
            id="pref-label-as-list",
        ),
        pytest.param(
            _concept(1, prefLabel={"en": "Topic"}),
            [
                (
                    "theme.https://mex.rki.de/item/theme-1.prefLabel: "
                    "'de' is a required property"
                )
            ],
            id="pref-label-missing-language",
        ),
        pytest.param(
            _concept(1, definition=[{"fr": "Sujet"}]),
            [
                (
                    "theme.https://mex.rki.de/item/theme-1.definition.0: "
                    "Additional properties are not allowed ('fr' was unexpected)"
                )
            ],
            id="unknown-language",
        ),
        pytest.param(
            _concept(1, entityType="Concept"),
            [
                (
                    "theme.https://mex.rki.de/item/theme-1: "
                    "Additional properties are not allowed ('entityType' was unexpected)"
                )
            ],
            id="unknown-property",
        ),
        pytest.param(
            {"inScheme": THEME, "prefLabel": LABEL},
            ["theme.<no identifier>: 'identifier' is a required property"],
            id="missing-identifier",
        ),
    ],
)
def test_concept_schema_violations_are_detected(
    validators: tuple[Draft202012Validator, Draft202012Validator],
    concept: dict[str, Any],
    expected: list[str],
) -> None:
    concept_validator, _ = validators
    violations = find_concept_schema_violations({"theme": [concept]}, concept_validator)
    assert violations == expected


@pytest.mark.parametrize(
    ("scheme", "expected"),
    [
        pytest.param(
            {"identifier": THEME, "label": "Theme vocabulary", "description": LABEL},
            [],
            id="valid-scheme",
        ),
        pytest.param(
            {"identifier": THEME, "label": "Theme vocabulary", "description": "x"},
            [f"concept-schemes.{THEME}.description: 'x' is not of type 'object'"],
            id="description-as-string",
        ),
        pytest.param(
            {"identifier": THEME},
            [f"concept-schemes.{THEME}: 'label' is a required property"],
            id="missing-label",
        ),
        pytest.param(
            {"label": "Theme vocabulary"},
            ["concept-schemes.<no identifier>: 'identifier' is a required property"],
            id="missing-identifier",
        ),
    ],
)
def test_concept_scheme_schema_violations_are_detected(
    validators: tuple[Draft202012Validator, Draft202012Validator],
    scheme: dict[str, Any],
    expected: list[str],
) -> None:
    _, scheme_validator = validators
    violations = find_concept_scheme_schema_violations([scheme], scheme_validator)
    assert violations == expected


def test_duplicate_concept_scheme_violations_are_detected() -> None:
    schemes = [{"identifier": THEME}, {"identifier": "b"}, {"identifier": THEME}]
    assert find_duplicate_concept_scheme_violations(schemes) == [
        f"concept-schemes: duplicate identifier {THEME!r}"
    ]
    assert find_duplicate_concept_scheme_violations(schemes[:2]) == []


def test_unbacked_concept_scheme_violations_are_detected() -> None:
    orphan = "https://mex.rki.de/item/orphan"
    violations = find_unbacked_concept_scheme_violations({"theme"}, {THEME, orphan})
    assert violations == [f"concept-schemes: {orphan!r} has no vocabulary file"]
    assert find_unbacked_concept_scheme_violations({"theme"}, {THEME}) == []


@pytest.mark.parametrize(
    ("concept", "expected"),
    [
        pytest.param(_concept(1), [], id="member-of-own-scheme"),
        pytest.param(
            _concept(1, inScheme="https://mex.rki.de/item/other"),
            [
                (
                    f"theme.{THEME}-1: inScheme is 'https://mex.rki.de/item/other', "
                    f"expected {THEME!r}"
                )
            ],
            id="foreign-in-scheme",
        ),
        pytest.param(
            {"identifier": "https://mex.rki.de/item/other-1", "inScheme": THEME},
            [
                (
                    "theme.https://mex.rki.de/item/other-1: identifier does not "
                    f"start with {THEME + '-'!r}"
                )
            ],
            id="foreign-identifier-prefix",
        ),
    ],
)
def test_scheme_membership_violations_are_detected(
    concept: dict[str, Any], expected: list[str]
) -> None:
    assert find_scheme_membership_violations({"theme": [concept]}) == expected


@pytest.mark.parametrize(
    ("broader", "expected"),
    [
        pytest.param(f"{THEME}-2", [], id="resolves-as-string"),
        pytest.param([f"{THEME}-2"], [], id="resolves-as-list"),
        pytest.param(
            f"{THEME}-9",
            [f"theme.{THEME}-1: broader '{THEME}-9' not found in vocabulary 'theme'"],
            id="unresolved",
        ),
    ],
)
def test_unresolved_broader_violations_are_detected(
    broader: object, expected: list[str]
) -> None:
    vocabularies = {"theme": [_concept(1, broader=broader), _concept(2)]}
    assert find_unresolved_broader_violations(vocabularies) == expected


def test_duplicate_pref_label_violations_are_detected() -> None:
    vocabularies = {
        "theme": [
            _concept(1, prefLabel=LABEL),
            _concept(2, prefLabel={"de": "Anderes", "en": "Topic"}),
            _concept(3, prefLabel=[LABEL]),  # wrong shape, reported by the schema
        ]
    }
    assert find_duplicate_pref_label_violations(vocabularies) == [
        f"theme: prefLabel.en 'Topic' is used by ['{THEME}-1', '{THEME}-2']"
    ]


def test_shared_exact_match_warnings_are_reported() -> None:
    duration = "http://www.w3.org/2001/XMLSchema#duration"
    vocabularies = {
        "theme": [
            _concept(8, exactMatch=[duration]),
            _concept(14, exactMatch=[duration]),
            _concept(15, exactMatch=["http://www.w3.org/2001/XMLSchema#gYearMonth"]),
        ]
    }
    assert find_shared_exact_match_warnings(vocabularies) == [
        f"theme: exactMatch {duration!r} is shared by ['{THEME}-8', '{THEME}-14']"
    ]
    assert find_shared_exact_match_warnings({"theme": vocabularies["theme"][1:]}) == []
