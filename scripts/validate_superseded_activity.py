"""Build a real jsonschema validator for merged-activity's if/then conditional.

mex-model has never run instance-level JSON Schema validation anywhere -
`check_schemas.py`-style checks only validate the schema *documents*
themselves, not example data. These helpers build a `referencing.Registry`
that resolves mex-model's cross-file `$ref`s, including the non-standard
`#/identifier` fragment convention documented by each schema's `$$target`,
so that `merged-activity.json`'s if/then conditional (full fields required
when active, only identifier+supersededBy when superseded) can actually be
exercised with real data. Imported by tests/test_validate_superseded_activity.py.
"""

from copy import deepcopy
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from mex.model import FIELD_JSON_BY_NAME, MERGED_MODEL_JSON_BY_NAME


def with_synthetic_identifier_pointer(schema: dict[str, Any]) -> dict[str, Any]:
    """Add a top-level `identifier` key mirroring `properties.identifier`.

    Other entity schemas reference this document as `<id>#/identifier`, which
    only resolves as a standard JSON Pointer if `identifier` exists at the
    document root. `$$target` documents this convention but nothing
    currently implements it, so we synthesize it here purely for validation.
    """
    patched = deepcopy(schema)
    patched["identifier"] = patched["properties"]["identifier"]
    return patched


def build_registry() -> Registry:
    """Build a referencing.Registry covering every merged entity and field."""
    resources = [
        Resource.from_contents(schema, default_specification=DRAFT202012)
        for schema in FIELD_JSON_BY_NAME.values()
    ]
    resources += [
        Resource.from_contents(
            with_synthetic_identifier_pointer(schema),
            default_specification=DRAFT202012,
        )
        for schema in MERGED_MODEL_JSON_BY_NAME.values()
    ]
    return Registry().with_resources(
        (resource_id, resource)
        for resource in resources
        if (resource_id := resource.id()) is not None
    )


def build_activity_validator() -> Draft202012Validator:
    """Build a validator for merged-activity.json's if/then conditional schema."""
    registry = build_registry()
    schema = with_synthetic_identifier_pointer(MERGED_MODEL_JSON_BY_NAME["activity"])
    return Draft202012Validator(schema, registry=registry)
