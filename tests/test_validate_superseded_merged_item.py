from typing import Any

import pytest
from jsonschema import Draft202012Validator

from mex.model import EXTRACTED_MODEL_JSON_BY_NAME, MERGED_MODEL_JSON_BY_NAME

IDENTIFIER = "gglGQVGwZNJtqYDkW4N8jL"
SUPERSEDED_BY = "dYb6qKqjdpocTAUEPPTTj2"
REFERENCE = "fKJE3RzeJ6ntHtqsXOOQR8"
CONCEPT = "https://mex.rki.de/item/some-concept-3000"
TEXT = {"value": "This is an example text.", "language": "en"}

# a valid, non-empty value for every field that is required on an active item
ACTIVE_VALUE_BY_FIELD: dict[str, Any] = {
    "accessRestriction": CONCEPT,
    "contact": [REFERENCE],
    "containedBy": [REFERENCE],
    "creator": [REFERENCE],
    "description": [TEXT],
    "email": ["info@rki.de"],
    "fullName": ["Example, Person"],
    "hasConsentStatus": CONCEPT,
    "hasDataSubject": REFERENCE,
    "isIndicatedAtTime": "2022-09-30T20:48:35Z",
    "issued": "2024",
    "keyword": [TEXT],
    "label": [TEXT],
    "name": [TEXT],
    "officialName": [TEXT],
    "resourceCreationMethod": [CONCEPT],
    "responsibleUnit": [REFERENCE],
    "technicalAccessibility": CONCEPT,
    "theme": [CONCEPT],
    "title": [TEXT],
    "unitInCharge": [REFERENCE],
    "usedIn": [REFERENCE],
}

KEY_FIELDS = {"identifier", "supersededBy"}

PROVENANCE_FIELDS = {
    "hadPrimarySource",
    "identifier",
    "identifierInPrimarySource",
    "stableTargetId",
}

ENTITY_NAMES = sorted(MERGED_MODEL_JSON_BY_NAME)


def gated_field_names(entity_name: str) -> list[str]:
    """Fields required on an active merged item, taken from the extracted schema."""
    extracted_schema = EXTRACTED_MODEL_JSON_BY_NAME[entity_name]
    return sorted(set(extracted_schema["required"]) - PROVENANCE_FIELDS)


def non_key_field_names(entity_name: str) -> list[str]:
    """Fields a superseded merged item must leave at their default."""
    return sorted(
        set(MERGED_MODEL_JSON_BY_NAME[entity_name]["properties"]) - KEY_FIELDS
    )


def is_array_field(entity_name: str, field_name: str) -> bool:
    definition = MERGED_MODEL_JSON_BY_NAME[entity_name]["properties"][field_name]
    return bool(definition.get("type") == "array")


def empty_value(entity_name: str, field_name: str) -> list[Any] | None:
    """Return the default value a superseded item carries for a field."""
    return [] if is_array_field(entity_name, field_name) else None


GATED_FIELD_PARAMS = [
    pytest.param(entity_name, field_name, id=f"{entity_name}-{field_name}")
    for entity_name in ENTITY_NAMES
    for field_name in gated_field_names(entity_name)
]

NON_KEY_FIELD_PARAMS = [
    pytest.param(entity_name, field_name, id=f"{entity_name}-{field_name}")
    for entity_name in ENTITY_NAMES
    for field_name in non_key_field_names(entity_name)
]


def active_instance(entity_name: str) -> dict[str, Any]:
    return {
        "identifier": IDENTIFIER,
        "supersededBy": None,
        **{
            field_name: ACTIVE_VALUE_BY_FIELD[field_name]
            for field_name in gated_field_names(entity_name)
        },
    }


def failed_keywords(
    validator: Draft202012Validator, instance: dict[str, Any]
) -> set[str]:
    return {str(error.validator) for error in validator.iter_errors(instance)}


def failed_else_fields(
    validator: Draft202012Validator, instance: dict[str, Any]
) -> set[str]:
    """Return the fields rejected by the gate's else branch, i.e. as tombstone."""
    return {
        str(error.absolute_schema_path[4])
        for error in validator.iter_errors(instance)
        if list(error.absolute_schema_path)[:4]
        == [
            "allOf",
            0,
            "else",
            "properties",
        ]
    }


@pytest.mark.parametrize("entity_name", ENTITY_NAMES)
def test_merged_schema_gates_extracted_required_fields(entity_name: str) -> None:
    merged_schema = MERGED_MODEL_JSON_BY_NAME[entity_name]
    assert merged_schema["required"] == ["identifier"]
    (gate,) = merged_schema["allOf"]
    assert gate["if"] == {"properties": {"supersededBy": {"type": "null"}}}
    assert sorted(gate["then"]["required"]) == gated_field_names(entity_name)
    assert sorted(gate["then"]["properties"]) == gated_field_names(entity_name)
    assert sorted(gate["else"]["properties"]) == non_key_field_names(entity_name)


@pytest.mark.parametrize("entity_name", ENTITY_NAMES)
def test_active_item_with_all_required_fields_is_valid(
    merged_validators: dict[str, Draft202012Validator], entity_name: str
) -> None:
    assert failed_keywords(
        merged_validators[entity_name], active_instance(entity_name)
    ) == (set())


@pytest.mark.parametrize("entity_name", ENTITY_NAMES)
def test_tombstone_with_identifier_and_superseded_by_only_is_valid(
    merged_validators: dict[str, Draft202012Validator], entity_name: str
) -> None:
    instance = {"identifier": IDENTIFIER, "supersededBy": SUPERSEDED_BY}
    assert failed_keywords(merged_validators[entity_name], instance) == set()


@pytest.mark.parametrize("entity_name", ENTITY_NAMES)
def test_tombstone_with_default_values_is_valid(
    merged_validators: dict[str, Draft202012Validator], entity_name: str
) -> None:
    instance = {
        "identifier": IDENTIFIER,
        "supersededBy": SUPERSEDED_BY,
        **{
            field_name: empty_value(entity_name, field_name)
            for field_name in non_key_field_names(entity_name)
        },
    }
    assert failed_keywords(merged_validators[entity_name], instance) == set()


@pytest.mark.parametrize(("entity_name", "field_name"), NON_KEY_FIELD_PARAMS)
def test_tombstone_with_leftover_value_is_invalid(
    merged_validators: dict[str, Draft202012Validator],
    entity_name: str,
    field_name: str,
) -> None:
    leftover = ["leftover"] if is_array_field(entity_name, field_name) else "leftover"
    instance = {
        "identifier": IDENTIFIER,
        "supersededBy": SUPERSEDED_BY,
        field_name: leftover,
    }
    assert failed_else_fields(merged_validators[entity_name], instance) == {field_name}


@pytest.mark.parametrize("entity_name", ENTITY_NAMES)
def test_fully_populated_item_with_superseded_by_is_invalid(
    merged_validators: dict[str, Draft202012Validator], entity_name: str
) -> None:
    instance = {**active_instance(entity_name), "supersededBy": SUPERSEDED_BY}
    assert failed_else_fields(merged_validators[entity_name], instance) == set(
        gated_field_names(entity_name)
    )


@pytest.mark.parametrize("entity_name", ENTITY_NAMES)
def test_tombstone_missing_identifier_is_invalid(
    merged_validators: dict[str, Draft202012Validator], entity_name: str
) -> None:
    instance = {"supersededBy": SUPERSEDED_BY}
    assert "required" in failed_keywords(merged_validators[entity_name], instance)


@pytest.mark.parametrize(("entity_name", "field_name"), GATED_FIELD_PARAMS)
@pytest.mark.parametrize(
    "superseded_by",
    [pytest.param(None, id="null"), pytest.param("__ABSENT__", id="absent")],
)
def test_active_item_missing_required_field_is_invalid(
    merged_validators: dict[str, Draft202012Validator],
    entity_name: str,
    field_name: str,
    superseded_by: str | None,
) -> None:
    instance = active_instance(entity_name)
    instance.pop(field_name)
    if superseded_by == "__ABSENT__":
        instance.pop("supersededBy")
    assert failed_keywords(merged_validators[entity_name], instance) == {"required"}


@pytest.mark.parametrize(("entity_name", "field_name"), GATED_FIELD_PARAMS)
def test_active_item_with_empty_required_field_is_invalid(
    merged_validators: dict[str, Draft202012Validator],
    entity_name: str,
    field_name: str,
) -> None:
    instance = active_instance(entity_name)
    instance[field_name] = empty_value(entity_name, field_name)
    expected = "minItems" if instance[field_name] == [] else "not"
    assert failed_keywords(merged_validators[entity_name], instance) == {expected}
