from collections.abc import Mapping

import pytest
from check_schemas import (
    find_malformed_msgid_violations,
    find_misplaced_translation_violations,
    find_missing_entity_label_violations,
    find_missing_plural_translation_violations,
    find_missing_translation_violations,
)


@pytest.mark.parametrize(
    ("field_names_by_entity", "po_data_by_language", "expected"),
    [
        pytest.param(
            {"Resource": {"missingField"}},
            {"en": 'msgid "otherField.singular"\nmsgstr "Other"\n'},
            [
                "en: no translation found for Resource.missingField.singular",
                "en: no translation found for Resource.missingField.description",
            ],
            id="missing-translation",
        ),
        pytest.param(
            {"Resource": {"missingField"}},
            {
                "de": 'msgid "otherField.singular"\nmsgstr "Andere"\n',
                "en": 'msgid "otherField.singular"\nmsgstr "Other"\n',
            },
            [
                "de: no translation found for Resource.missingField.singular",
                "de: no translation found for Resource.missingField.description",
                "en: no translation found for Resource.missingField.singular",
                "en: no translation found for Resource.missingField.description",
            ],
            id="missing-in-every-language",
        ),
        pytest.param(
            {"Resource": {"abstract"}},
            {
                "en": 'msgid "abstract.singular"\nmsgstr "Abstract"\n'
                "\n"
                'msgid "abstract.description"\nmsgstr "Summary"\n'
            },
            [],
            id="matches-singular-and-description",
        ),
        pytest.param(
            {"Resource": {"abstract"}},
            {"en": 'msgid "abstract.singular"\nmsgstr "Abstract"\n'},
            ["en: no translation found for Resource.abstract.description"],
            id="label-without-description",
        ),
        pytest.param(
            {"Resource": {"abstract"}},
            {"en": 'msgid "abstract.description"\nmsgstr "Summary"\n'},
            ["en: no translation found for Resource.abstract.singular"],
            id="description-without-label",
        ),
        pytest.param(
            {"Resource": {"abstract"}},
            {"en": 'msgid "abstract.plural"\nmsgstr "Abstracts"\n'},
            [
                "en: no translation found for Resource.abstract.singular",
                "en: no translation found for Resource.abstract.description",
            ],
            id="other-suffix-does-not-count",
        ),
        pytest.param(
            {"Resource": {"supersededBy"}},
            {
                "en": 'msgid "supersededBy"\nmsgstr "superseded by"\n'
                "\n"
                'msgid "supersededBy.description"\nmsgstr "Preferred duplicate"\n'
            },
            [],
            id="matches-exact-msgid-as-label",
        ),
        pytest.param(
            {"ResourceSeries": {"accrualPeriodicity"}},
            {
                "en": 'msgctxt "ResourceSeries"\n'
                'msgid "accrualPeriodicity.singular"\n'
                'msgstr "Update frequency"\n'
                "\n"
                'msgctxt "ResourceSeries"\n'
                'msgid "accrualPeriodicity.description"\n'
                'msgstr "How often the collection is updated"\n'
            },
            [],
            id="matches-own-context",
        ),
        pytest.param(
            {"ResourceSeries": {"accrualPeriodicity"}},
            {
                "en": 'msgid "accrualPeriodicity.singular"\n'
                'msgstr "Update frequency"\n'
                "\n"
                'msgctxt "Resource"\n'
                'msgid "accrualPeriodicity.description"\n'
                'msgstr "How often the data is updated"\n'
            },
            [
                (
                    "en: no translation found for "
                    "ResourceSeries.accrualPeriodicity.description"
                )
            ],
            id="ignores-other-entities-context",
        ),
        pytest.param(
            {"Resource": {"abstract"}, "ResourceSeries": {"abstract"}},
            {
                "en": 'msgctxt "Resource"\n'
                'msgid "abstract.description"\n'
                'msgstr "Summary of the data"\n'
                "\n"
                'msgid "abstract.singular"\n'
                'msgstr "Abstract"\n'
            },
            ["en: no translation found for ResourceSeries.abstract.description"],
            id="context-resets-on-blank-line",
        ),
        pytest.param(
            {"Resource": {"abstract"}},
            {
                "en": 'msgid "abstract.singular"\nmsgstr ""\n'
                "\n"
                'msgid "abstract.description"\nmsgstr ""\n'
            },
            [
                "en: no translation found for Resource.abstract.singular",
                "en: no translation found for Resource.abstract.description",
            ],
            id="empty-msgstr-counts-as-missing",
        ),
        pytest.param(
            {"Resource": {"abstract"}},
            {
                "en": 'msgid "abstract.singular"\nmsgstr ""\n"Abs"\n"tract"\n'
                "\n"
                'msgid "abstract.description"\nmsgstr "Summary"\n'
            },
            [],
            id="multi-line-msgstr-is-not-empty",
        ),
    ],
)
def test_missing_translation_violations_are_detected(
    field_names_by_entity: Mapping[str, set[str]],
    po_data_by_language: dict[str, str],
    expected: list[str],
) -> None:
    violations = find_missing_translation_violations(
        field_names_by_entity, po_data_by_language
    )
    assert violations == expected


@pytest.mark.parametrize(
    ("array_field_names_by_entity", "po_data_by_language", "expected"),
    [
        pytest.param(
            {"Resource": {"keyword"}},
            {
                "en": 'msgid "keyword.singular"\n'
                'msgid_plural "keyword.plural"\n'
                'msgstr[0] "Keyword"\n'
                'msgstr[1] "Keywords"\n'
            },
            [],
            id="plural-present",
        ),
        pytest.param(
            {"Resource": {"keyword"}},
            {"en": 'msgid "keyword.singular"\nmsgstr "Keyword"\n'},
            ["en: no plural translation found for Resource.keyword.plural"],
            id="singular-only",
        ),
        pytest.param(
            {"Resource": {"keyword"}},
            {"en": 'msgid "keyword.plural"\nmsgstr "Keywords"\n'},
            ["en: no plural translation found for Resource.keyword.plural"],
            id="standalone-plural-msgid-does-not-count",
        ),
        pytest.param(
            {"Resource": {"keyword"}},
            {
                "en": 'msgid "keyword.singular"\n'
                'msgid_plural "keywords"\n'
                'msgstr[0] "Keyword"\n'
                'msgstr[1] "Keywords"\n'
            },
            ["en: no plural translation found for Resource.keyword.plural"],
            id="wrong-msgid-plural",
        ),
        pytest.param(
            {"Resource": {"keyword"}, "ResourceSeries": {"keyword"}},
            {
                "de": 'msgid "keyword.singular"\n'
                'msgid_plural "keyword.plural"\n'
                'msgstr[0] "Schlagwort"\n'
                'msgstr[1] "Schlagwörter"\n',
                "en": 'msgctxt "Resource"\n'
                'msgid "keyword.singular"\n'
                'msgid_plural "keyword.plural"\n'
                'msgstr[0] "Keyword"\n'
                'msgstr[1] "Keywords"\n',
            },
            ["en: no plural translation found for ResourceSeries.keyword.plural"],
            id="ignores-other-entities-context",
        ),
        pytest.param(
            {"Resource": {"keyword"}},
            {
                "en": 'msgctxt "Resource"\n'
                'msgid "abstract.singular"\n'
                'msgstr "Abstract"\n'
                "\n"
                'msgid "keyword.singular"\n'
                'msgid_plural "keyword.plural"\n'
                'msgstr[0] "Keyword"\n'
                'msgstr[1] "Keywords"\n'
            },
            [],
            id="context-resets-on-blank-line",
        ),
        pytest.param(
            {"Resource": {"keyword"}},
            {
                "en": 'msgid "keyword.singular"\n'
                'msgid_plural "keyword.plural"\n'
                'msgstr[0] "Keyword"\n'
                'msgstr[1] ""\n'
            },
            ["en: no plural translation found for Resource.keyword.plural"],
            id="empty-plural-form-counts-as-missing",
        ),
    ],
)
def test_missing_plural_translation_violations_are_detected(
    array_field_names_by_entity: Mapping[str, set[str]],
    po_data_by_language: dict[str, str],
    expected: list[str],
) -> None:
    violations = find_missing_plural_translation_violations(
        array_field_names_by_entity, po_data_by_language
    )
    assert violations == expected


@pytest.mark.parametrize(
    ("entity_names", "po_data_by_language", "expected"),
    [
        pytest.param(
            {"ResourceSeries"},
            {"en": 'msgid "ResourceSeries"\nmsgstr "Collection"\n'},
            [],
            id="entity-label-present",
        ),
        pytest.param(
            {"ResourceSeries"},
            {"en": 'msgid "Resource Series"\nmsgstr "Collection"\n'},
            ["en: no translation found for entity 'ResourceSeries'"],
            id="entity-label-msgid-does-not-match-entity-name",
        ),
        pytest.param(
            {"ResourceSeries"},
            {"en": 'msgctxt "Resource"\nmsgid "ResourceSeries"\nmsgstr "Collection"\n'},
            ["en: no translation found for entity 'ResourceSeries'"],
            id="entity-label-must-be-context-free",
        ),
        pytest.param(
            {"ResourceSeries"},
            {"en": 'msgid "ResourceSeries"\nmsgstr ""\n'},
            ["en: no translation found for entity 'ResourceSeries'"],
            id="entity-label-empty",
        ),
    ],
)
def test_missing_entity_label_violations_are_detected(
    entity_names: set[str],
    po_data_by_language: dict[str, str],
    expected: list[str],
) -> None:
    violations = find_missing_entity_label_violations(entity_names, po_data_by_language)
    assert violations == expected


@pytest.mark.parametrize(
    ("field_names_by_entity", "po_data_by_language", "expected"),
    [
        pytest.param(
            {"Activity": {"title"}, "BibliographicResource": {"isbnIssn"}},
            {"en": 'msgctxt "Activity"\nmsgid "isbnIssn.singular"\nmsgstr "ISBN"\n'},
            [
                (
                    "en: msgctxt 'Activity' has msgid 'isbnIssn.singular' "
                    "but Activity has no field isbnIssn"
                )
            ],
            id="field-not-on-context-entity",
        ),
        pytest.param(
            {"Activity": {"title"}},
            {"en": 'msgctxt "Activiti"\nmsgid "title.singular"\nmsgstr "Title"\n'},
            ["en: msgctxt 'Activiti' is not a known entity (msgid 'title.singular')"],
            id="unknown-context",
        ),
        pytest.param(
            {"Activity": {"title"}},
            {"en": 'msgctxt "Activity"\nmsgid "title.singular"\nmsgstr "Title"\n'},
            [],
            id="field-on-context-entity",
        ),
        pytest.param(
            {"Activity": {"title"}},
            {"en": 'msgid "entityName.singular"\nmsgstr "Type"\n'},
            [],
            id="context-free-msgid-is-ignored",
        ),
    ],
)
def test_misplaced_translation_violations_are_detected(
    field_names_by_entity: Mapping[str, set[str]],
    po_data_by_language: dict[str, str],
    expected: list[str],
) -> None:
    violations = find_misplaced_translation_violations(
        field_names_by_entity, po_data_by_language
    )
    assert violations == expected


@pytest.mark.parametrize(
    ("po_data_by_language", "expected"),
    [
        pytest.param(
            {
                "en": 'msgid "Resource"\nmsgstr "Resource"\n'
                "\n"
                'msgid "title.description"\nmsgstr "Name"\n'
                "\n"
                'msgid "keyword.singular"\n'
                'msgid_plural "keyword.plural"\n'
                'msgstr[0] "Keyword"\n'
                'msgstr[1] "Keywords"\n'
            },
            [],
            id="well-formed",
        ),
        pytest.param(
            {"en": 'msgctxt "Activity"\nmsgid "title.singluar"\nmsgstr "Title"\n'},
            ["en: msgid 'title.singluar' has invalid suffix 'singluar'"],
            id="invalid-suffix",
        ),
        pytest.param(
            {
                "en": 'msgid "keyword.singular"\n'
                'msgid_plural "keywords.plural"\n'
                'msgstr[0] "Keyword"\n'
                'msgstr[1] "Keywords"\n'
            },
            [
                (
                    "en: msgid 'keyword.singular' has msgid_plural 'keywords.plural', "
                    "expected 'keyword.plural'"
                )
            ],
            id="mismatched-msgid-plural",
        ),
        pytest.param(
            {
                "en": 'msgid "keyword.description"\n'
                'msgid_plural "keyword.plural"\n'
                'msgstr[0] "Keyword"\n'
                'msgstr[1] "Keywords"\n'
            },
            [
                (
                    "en: msgid 'keyword.description' has a msgid_plural but is not "
                    "a .singular msgid"
                )
            ],
            id="msgid-plural-on-non-singular",
        ),
    ],
)
def test_malformed_msgid_violations_are_detected(
    po_data_by_language: dict[str, str], expected: list[str]
) -> None:
    violations = find_malformed_msgid_violations(po_data_by_language)
    assert violations == expected
