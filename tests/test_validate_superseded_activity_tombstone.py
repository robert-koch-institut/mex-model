from typing import Any

import pytest
from jsonschema import Draft202012Validator
from validate_superseded_activity_tombstone import build_activity_tombstone_validator

ACTIVE_VALID = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
    "contact": ["fKJE3RzeJ6ntHtqsXOOQR8"],
    "responsibleUnit": ["fKJE3RzeJ6ntHtqsXOOQR8"],
    "title": [{"value": "An active activity"}],
}

ACTIVE_MISSING_CONTACT = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
    "responsibleUnit": ["fKJE3RzeJ6ntHtqsXOOQR8"],
    "title": [{"value": "An active activity missing contact"}],
}

ACTIVE_WITH_STRAY_SUPERSEDEDBY = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
    "contact": ["fKJE3RzeJ6ntHtqsXOOQR8"],
    "responsibleUnit": ["fKJE3RzeJ6ntHtqsXOOQR8"],
    "title": [{"value": "Active but also carries a supersededBy key"}],
    "supersededBy": None,
}

TOMBSTONE_VALID = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
    "supersededBy": "dYb6qKqjdpocTAUEPPTTj2",
}

TOMBSTONE_MISSING_SUPERSEDEDBY = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
}

TOMBSTONE_WITH_STRAY_TITLE = {
    "identifier": "gglGQVGwZNJtqYDkW4N8jL",
    "supersededBy": "dYb6qKqjdpocTAUEPPTTj2",
    "title": [{"value": "Stale title carried over from before superseding"}],
}


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    return build_activity_tombstone_validator()


@pytest.mark.parametrize(
    ("instance", "expected_valid"),
    [
        pytest.param(ACTIVE_VALID, True, id="active-all-required-fields-set"),
        pytest.param(ACTIVE_MISSING_CONTACT, False, id="active-missing-contact"),
        pytest.param(
            ACTIVE_WITH_STRAY_SUPERSEDEDBY,
            False,
            id="active-stray-supersededby-key-is-forbidden",
        ),
        pytest.param(
            TOMBSTONE_VALID,
            True,
            id="tombstone-identifier-and-supersededby-only",
        ),
        pytest.param(
            TOMBSTONE_MISSING_SUPERSEDEDBY,
            False,
            id="tombstone-missing-supersededby",
        ),
        pytest.param(
            TOMBSTONE_WITH_STRAY_TITLE,
            False,
            id="tombstone-stray-stale-title-is-forbidden",
        ),
    ],
)
def test_merged_activity_tombstone_validation(
    validator: Draft202012Validator,
    instance: dict[str, Any],
    expected_valid: bool,  # noqa: FBT001
) -> None:
    # oneOf error messages don't name a specific failing keyword the way
    # if/then's do (see test_validate_superseded_activity.py), so this only
    # asserts overall validity rather than the precise failure reason.
    assert validator.is_valid(instance) is expected_valid
