from collections.abc import Mapping

import pytest
from check_schemas import (
    find_missing_entity_label_violations,
    find_missing_translation_violations,
)


@pytest.mark.parametrize(
    ("field_names_by_entity", "po_data_by_language", "expected"),
    [
        pytest.param(
            {"Resource": {"missingField"}},
            {"en": 'msgid "otherField.singular"\nmsgstr "Other"\n'},
            ["en: no translation found for field Resource.missingField"],
            id="missing-translation",
        ),
        pytest.param(
            {"Resource": {"missingField"}},
            {
                "de": 'msgid "otherField.singular"\nmsgstr "Andere"\n',
                "en": 'msgid "otherField.singular"\nmsgstr "Other"\n',
            },
            [
                "de: no translation found for field Resource.missingField",
                "en: no translation found for field Resource.missingField",
            ],
            id="missing-in-every-language",
        ),
        pytest.param(
            {"Resource": {"abstract"}},
            {"en": 'msgid "abstract.singular"\nmsgstr "Abstract"\n'},
            [],
            id="matches-suffixed-msgid",
        ),
        pytest.param(
            {"Resource": {"supersededBy"}},
            {"en": 'msgid "supersededBy"\nmsgstr "superseded by"\n'},
            [],
            id="matches-exact-msgid",
        ),
        pytest.param(
            {"ResourceSeries": {"accrualPeriodicity"}},
            {
                "en": 'msgctxt "ResourceSeries"\n'
                'msgid "accrualPeriodicity.singular"\n'
                'msgstr "Update frequency"\n'
            },
            [],
            id="matches-own-context",
        ),
        pytest.param(
            {"ResourceSeries": {"accrualPeriodicity"}},
            {
                "en": 'msgctxt "Resource"\n'
                'msgid "accrualPeriodicity.singular"\n'
                'msgstr "Update frequency"\n'
            },
            ["en: no translation found for field ResourceSeries.accrualPeriodicity"],
            id="ignores-other-entities-context",
        ),
        pytest.param(
            {"Resource": {"abstract"}, "ResourceSeries": {"abstract"}},
            {
                "en": 'msgctxt "Resource"\n'
                'msgid "abstract.singular"\n'
                'msgstr "Abstract"\n'
                "\n"
                'msgctxt "ResourceSeries"\n'
                'msgid "abstract.singular"\n'
                'msgstr "Abstract"\n'
            },
            [],
            id="context-resets-on-blank-line",
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
    ],
)
def test_missing_entity_label_violations_are_detected(
    entity_names: set[str],
    po_data_by_language: dict[str, str],
    expected: list[str],
) -> None:
    violations = find_missing_entity_label_violations(entity_names, po_data_by_language)
    assert violations == expected
