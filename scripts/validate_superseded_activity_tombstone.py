"""Build a real jsonschema validator for the generalized tombstone shape.

Companion to validate_superseded_activity.py. Where that module proves the
if/then approach on the real merged-activity.json (required-ness becomes
conditional, but every other field stays *allowed* on a superseded item),
this module proves the alternative: a superseded item's shape becomes a
completely separate schema - the shared mex/model/entities/tombstone.json -
so stray/stale data in any other field is rejected outright, not just
tolerated.

merged-activity.json on disk is NOT modified for this. Its "active" shape is
reconstructed in memory here (its current if/then version minus
supersededBy, with minItems restored) and combined with the shared
tombstone.json via oneOf. Imported by
tests/test_validate_superseded_activity_tombstone.py.
"""

import json
from copy import deepcopy
from importlib.resources import files
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from mex.model import FIELD_JSON_BY_NAME, MERGED_MODEL_JSON_BY_NAME

TOMBSTONE_SCHEMA: dict[str, Any] = json.loads(
    files("mex.model.entities").joinpath("tombstone.json").read_text("utf-8")
)


def with_synthetic_identifier_pointer(schema: dict[str, Any]) -> dict[str, Any]:
    """Add a top-level `identifier` key mirroring `properties.identifier`.

    Same fixup as in validate_superseded_activity.py: other entity schemas
    reference merged-* documents as `<id>#/identifier`, which only resolves
    as a standard JSON Pointer if `identifier` exists at the document root.
    """
    patched = deepcopy(schema)
    patched["identifier"] = patched["properties"]["identifier"]
    return patched


def build_active_shape() -> dict[str, Any]:
    """Reconstruct Activity's "active" shape: today's schema minus if/then.

    Starts from the on-disk (if/then) merged-activity.json, drops
    `supersededBy` entirely (an active item shouldn't carry the key at all
    in this design), drops the if/then keys, and restores unconditional
    `minItems`/`required` on contact/responsibleUnit/title.
    """
    active: dict[str, Any] = deepcopy(MERGED_MODEL_JSON_BY_NAME["activity"])
    del active["properties"]["supersededBy"]
    del active["if"]
    del active["then"]
    for field in ("contact", "responsibleUnit", "title"):
        active["properties"][field]["minItems"] = 1
    active["required"] = ["identifier", "contact", "responsibleUnit", "title"]
    return active


def build_registry() -> Registry:
    """Build a referencing.Registry covering fields, merged entities, and tombstone."""
    resources = [
        Resource.from_contents(schema, default_specification=DRAFT202012)
        for schema in FIELD_JSON_BY_NAME.values()
    ]
    resources += [
        Resource.from_contents(
            with_synthetic_identifier_pointer(schema),
            default_specification=DRAFT202012,
        )
        for name, schema in MERGED_MODEL_JSON_BY_NAME.items()
        if name != "activity"  # the root schema itself is passed separately
    ]
    resources.append(
        Resource.from_contents(TOMBSTONE_SCHEMA, default_specification=DRAFT202012)
    )
    return Registry().with_resources(
        (resource_id, resource)
        for resource in resources
        if (resource_id := resource.id()) is not None
    )


def build_root_schema() -> dict[str, Any]:
    """Build the oneOf[active, tombstone] root schema for MergedActivity."""
    return {
        "$id": "https://mex.rki.de/mex/model/entities/merged-activity-tombstone-demo",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Merged Activity (oneOf active/tombstone prototype)",
        "oneOf": [
            {"$ref": "#/$defs/active"},
            {"$ref": "https://mex.rki.de/mex/model/entities/tombstone"},
        ],
        "$defs": {"active": build_active_shape()},
    }


def build_activity_tombstone_validator() -> Draft202012Validator:
    """Build a validator for the oneOf[active, tombstone] MergedActivity shape."""
    registry = build_registry()
    schema = build_root_schema()
    return Draft202012Validator(schema, registry=registry)
