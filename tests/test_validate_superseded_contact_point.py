from typing import Any

import pytest
from jsonschema import Draft202012Validator
from validate_superseded_contact_point import build_contact_point_validator

ACTIVE_VALID = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
    "email": ["info@rki.de"],
    "supersededBy": None,
}

ACTIVE_MISSING_EMAIL = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
    "supersededBy": None,
}

ACTIVE_EMPTY_EMAIL = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
    "email": [],
    "supersededBy": None,
}

TOMBSTONE_VALID = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
    "supersededBy": "dYb6qKqjdpocTAUEPPTTj2",
}

TOMBSTONE_MISSING_IDENTIFIER = {
    "supersededBy": "dYb6qKqjdpocTAUEPPTTj2",
}

TOMBSTONE_EMPTY_EMAIL_ALLOWED = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
    "email": [],
    "supersededBy": "dYb6qKqjdpocTAUEPPTTj2",
}


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    return build_contact_point_validator()


@pytest.mark.parametrize(
    ("instance", "expected_valid", "expected_failed_keyword"),
    [
        pytest.param(ACTIVE_VALID, True, None, id="active-all-required-fields-set"),
        pytest.param(
            ACTIVE_MISSING_EMAIL,
            False,
            "required",
            id="active-missing-email",
        ),
        pytest.param(
            ACTIVE_EMPTY_EMAIL,
            False,
            "minItems",
            id="active-email-present-but-empty",
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
            TOMBSTONE_EMPTY_EMAIL_ALLOWED,
            True,
            None,
            id="tombstone-empty-email-is-fine",
        ),
    ],
)
def test_merged_contact_point_conditional_validation(
    validator: Draft202012Validator,
    instance: dict[str, Any],
    expected_valid: bool,  # noqa: FBT001
    expected_failed_keyword: str | None,
) -> None:
    errors = list(validator.iter_errors(instance))
    assert (not errors) is expected_valid
    if expected_failed_keyword is not None:
        assert expected_failed_keyword in {error.validator for error in errors}
