from mex.model import (
    ENTITY_JSON_BY_NAME,
    EXTRACTED_MODEL_JSON_BY_NAME,
    FIELD_JSON_BY_NAME,
    MERGED_MODEL_JSON_BY_NAME,
    VOCABULARY_JSON_BY_NAME,
)


def test_extracted_model_json_by_name() -> None:
    assert len(EXTRACTED_MODEL_JSON_BY_NAME) == 42


def test_merged_model_json_by_name() -> None:
    assert len(MERGED_MODEL_JSON_BY_NAME) == 42


def test_field_json_by_name() -> None:
    assert len(FIELD_JSON_BY_NAME) == 42


def test_vocabulary_json_by_name() -> None:
    assert len(VOCABULARY_JSON_BY_NAME) == 42


def test_entity_json_by_name() -> None:
    assert ENTITY_JSON_BY_NAME == EXTRACTED_MODEL_JSON_BY_NAME
