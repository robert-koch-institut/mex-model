from pathlib import Path

from mex.model import (
    ENTITY_JSON_BY_NAME,
    EXTRACTED_MODEL_JSON_BY_NAME,
    FIELD_JSON_BY_NAME,
    MERGED_MODEL_JSON_BY_NAME,
    VOCABULARY_JSON_BY_NAME,
)

MODEL_ROOT = Path(__file__).resolve().parent.parent / "mex" / "model"


def test_extracted_model_json_by_name() -> None:
    # sanity check on count
    expected = len(list((MODEL_ROOT / "entities").glob("extracted-*.json")))
    assert len(EXTRACTED_MODEL_JSON_BY_NAME) == expected
    # spot check on content
    assert (
        EXTRACTED_MODEL_JSON_BY_NAME["bibliographic_resource"]["properties"][
            "stableTargetId"
        ]["$ref"]
        == "/mex/model/entities/merged-bibliographic-resource#/identifier"
    )


def test_merged_model_json_by_name() -> None:
    # sanity check on count
    expected = len(list((MODEL_ROOT / "entities").glob("merged-*.json")))
    assert len(MERGED_MODEL_JSON_BY_NAME) == expected
    # spot check on content
    assert (
        MERGED_MODEL_JSON_BY_NAME["primary_source"]["properties"]["unitInCharge"][
            "items"
        ]["$ref"]
        == "/mex/model/entities/merged-organizational-unit#/identifier"
    )


def test_field_json_by_name() -> None:
    # sanity check on count
    expected = len(list((MODEL_ROOT / "fields").glob("*.json")))
    assert len(FIELD_JSON_BY_NAME) == expected
    # spot check on content
    assert (
        FIELD_JSON_BY_NAME["link"]["properties"]["url"]["examples"][0]
        == "https://hello-world.org"
    )


def test_vocabulary_json_by_name() -> None:
    # sanity check on count
    expected = len(list((MODEL_ROOT / "vocabularies").glob("*.json")))
    assert len(VOCABULARY_JSON_BY_NAME) == expected
    # spot check on content
    assert (
        VOCABULARY_JSON_BY_NAME["api_type"][0]["identifier"]
        == "https://mex.rki.de/item/api-type-1"
    )


def test_entity_json_by_name() -> None:
    # bw-compat test
    assert ENTITY_JSON_BY_NAME == EXTRACTED_MODEL_JSON_BY_NAME
