import pytest
from check_schemas import find_missing_translation_violations


@pytest.mark.parametrize(
    ("field_names", "po_data_by_language", "expected"),
    [
        pytest.param(
            {"missingField"},
            {"en": 'msgid "otherField.singular"\nmsgstr "Other"\n'},
            ["en: no translation found for field 'missingField'"],
            id="missing-translation",
        ),
        pytest.param(
            {"missingField"},
            {
                "de": 'msgid "otherField.singular"\nmsgstr "Andere"\n',
                "en": 'msgid "otherField.singular"\nmsgstr "Other"\n',
            },
            [
                "de: no translation found for field 'missingField'",
                "en: no translation found for field 'missingField'",
            ],
            id="missing-in-every-language",
        ),
        pytest.param(
            {"abstract"},
            {"en": 'msgid "abstract.singular"\nmsgstr "Abstract"\n'},
            [],
            id="matches-suffixed-msgid",
        ),
        pytest.param(
            {"supersededBy"},
            {"en": 'msgid "supersededBy"\nmsgstr "superseded by"\n'},
            [],
            id="matches-exact-msgid",
        ),
    ],
)
def test_missing_translation_violations_are_detected(
    field_names: set[str],
    po_data_by_language: dict[str, str],
    expected: list[str],
) -> None:
    violations = find_missing_translation_violations(field_names, po_data_by_language)
    assert violations == expected
