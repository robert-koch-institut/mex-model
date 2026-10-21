import json
import sys
from copy import deepcopy
from importlib.resources import files
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from mex.model import FIELD_JSON_BY_NAME, MERGED_MODEL_JSON_BY_NAME

# the sphinx extensions live in `docs/_ext` and are imported by their bare module names,
# just like `conf.py` does it, so the extension folder has to be on the import path
DOCS_DIR = Path(__file__).resolve().parent.parent / "docs" / "_ext"
sys.path.insert(0, str(DOCS_DIR))

# the schema checks live in `scripts` and are imported by their bare module name,
# both here and by the pre-commit hook that runs them directly
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


def _with_synthetic_identifier_pointer(schema: dict[str, Any]) -> dict[str, Any]:
    """Add a top-level `identifier` key mirroring `properties.identifier`.

    Other entity schemas reference this document as `<id>#/identifier`, which
    only resolves as a standard JSON Pointer if `identifier` exists at the
    document root. `$$target` documents this convention but nothing
    currently implements it, so we synthesize it here purely for validation.
    """
    patched = deepcopy(schema)
    patched["identifier"] = patched["properties"]["identifier"]
    return patched


def _load_concept_schema() -> dict[str, Any]:
    """Load `concept.json`, which is referenced by concept-valued fields."""
    concept_file = files("mex.model.entities") / "concept.json"
    return dict(json.loads(concept_file.read_text("utf-8")))


def _build_registry() -> Registry:
    """Build a referencing.Registry covering every merged entity, concept and field."""
    resources = [
        Resource.from_contents(schema, default_specification=DRAFT202012)
        for schema in FIELD_JSON_BY_NAME.values()
    ]
    resources += [
        Resource.from_contents(
            _with_synthetic_identifier_pointer(schema),
            default_specification=DRAFT202012,
        )
        for schema in [*MERGED_MODEL_JSON_BY_NAME.values(), _load_concept_schema()]
    ]
    return Registry().with_resources(
        (resource_id, resource)
        for resource in resources
        if (resource_id := resource.id()) is not None
    )


@pytest.fixture(scope="session")
def merged_validators() -> dict[str, Draft202012Validator]:
    """Return real jsonschema validators for every `merged-*.json`, by entity name.

    The validators resolve mex-model's cross-file `$ref`s, including the
    non-standard `#/identifier` fragment convention, so that the merged
    schemas' supersededBy if/then gate can be exercised with real data.
    """
    registry = _build_registry()
    return {
        name: Draft202012Validator(
            _with_synthetic_identifier_pointer(schema), registry=registry
        )
        for name, schema in MERGED_MODEL_JSON_BY_NAME.items()
    }
