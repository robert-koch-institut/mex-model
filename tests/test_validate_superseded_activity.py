from typing import Any

import pytest
from jsonschema import Draft202012Validator
from validate_superseded_activity import build_activity_validator

ACTIVE_VALID = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
    "contact": ["fKJE3RzeJ6ntHtqsXOOQR8"],
    "responsibleUnit": ["fKJE3RzeJ6ntHtqsXOOQR8"],
    "title": [{"value": "An active activity"}],
    "supersededBy": None,
}

ACTIVE_MISSING_CONTACT = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
    "responsibleUnit": ["fKJE3RzeJ6ntHtqsXOOQR8"],
    "title": [{"value": "An active activity missing contact"}],
    "supersededBy": None,
}

ACTIVE_EMPTY_CONTACT = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
    "contact": [],
    "responsibleUnit": ["fKJE3RzeJ6ntHtqsXOOQR8"],
    "title": [{"value": "Present but empty contact list"}],
    "supersededBy": None,
}

TOMBSTONE_VALID = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
    "supersededBy": "dYb6qKqjdpocTAUEPPTTj2",
}

TOMBSTONE_MISSING_IDENTIFIER = {
    "supersededBy": "dYb6qKqjdpocTAUEPPTTj2",
}

TOMBSTONE_EMPTY_CONTACT_ALLOWED = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
    "contact": [],
    "supersededBy": "dYb6qKqjdpocTAUEPPTTj2",
}


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    return build_activity_validator()


@pytest.mark.parametrize(
    ("instance", "expected_valid", "expected_failed_keyword"),
    [
        pytest.param(ACTIVE_VALID, True, None, id="active-all-required-fields-set"),
        pytest.param(
            ACTIVE_MISSING_CONTACT,
            False,
            "required",
            id="active-missing-contact",
        ),
        pytest.param(
            ACTIVE_EMPTY_CONTACT,
            False,
            "minItems",
            id="active-contact-present-but-empty",
        ),
        pytest.param(
            TOMBSTONE_VALID,
            True,
            None,
            id="tombstone-identifier-and-supersededby-only",
        ),
        pytest.param(
            TOMBSTONE_MISSING_IDENTIFIER,
            False,
            "required",
            id="tombstone-missing-identifier",
        ),
        pytest.param(
            TOMBSTONE_EMPTY_CONTACT_ALLOWED,
            True,
            None,
            id="tombstone-empty-contact-is-fine",
        ),
    ],
)
def test_merged_activity_conditional_validation(
    validator: Draft202012Validator,
    instance: dict[str, Any],
    expected_valid: bool,  # noqa: FBT001
    expected_failed_keyword: str | None,
) -> None:
    errors = list(validator.iter_errors(instance))
    assert (not errors) is expected_valid
    if expected_failed_keyword is not None:
        assert expected_failed_keyword in {error.validator for error in errors}
