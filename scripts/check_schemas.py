"""Standalone schema-correctness checks for mex-model.

Run directly (`uv run python scripts/check_schemas.py`) or via the
`schema-checks` pre-commit hook. The same `find_*_violations` functions are
imported by the test suite for both real-data regression tests and
fixture-based self-tests.
"""

import json
import sys
from collections.abc import Iterable, Iterator
from importlib.resources import files
from typing import Any
from urllib.parse import urlparse

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from mex.model import (
    EXTRACTED_MODEL_JSON_BY_NAME,
    FIELD_JSON_BY_NAME,
    MERGED_MODEL_JSON_BY_NAME,
    VOCABULARY_JSON_BY_NAME,
)

EXCLUDED_PROVENANCE_FIELDS = frozenset(
    {"hadPrimarySource", "identifierInPrimarySource", "stableTargetId"}
)
ANNOTATION_URI_KEYS = ("closeMatch", "exactMatch", "sameAs", "subPropertyOf")


def _iter_use_scheme_nodes(node: object) -> Iterator[dict[str, Any]]:
    """Yield every dict with a `useScheme` key found anywhere in a json structure."""
    if isinstance(node, dict):
        if "useScheme" in node:
            yield node
        for value in node.values():
            yield from _iter_use_scheme_nodes(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_use_scheme_nodes(item)


def _iter_refs(node: object) -> Iterator[str]:
    """Yield all `$ref` values found anywhere in a json structure."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref":
                yield str(value)
            else:
                yield from _iter_refs(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_refs(item)


def _find_array_shape_violations(
    entity_name: str, name: str, definition: dict[str, Any], required: set[str]
) -> list[str]:
    """Check a single array property's minItems/required/default shape."""
    violations = []
    has_min_items = "minItems" in definition
    has_default = "default" in definition
    if has_min_items and name not in required:
        violations.append(f"{entity_name}.{name}: has minItems but is not in required")
    if not has_min_items and name in required:
        violations.append(f"{entity_name}.{name}: is required but has no minItems")
    if not has_min_items and not has_default:
        violations.append(f"{entity_name}.{name}: optional array is missing a default")
    return violations


def _find_optional_scalar_violations(
    entity_name: str, name: str, definition: dict[str, Any]
) -> list[str]:
    """Check a single optional scalar property's anyOf-null/default shape."""
    violations = []
    any_of = definition.get("anyOf", [])
    has_null_option = any(
        isinstance(option, dict) and option.get("type") == "null" for option in any_of
    )
    if not has_null_option:
        violations.append(
            f"{entity_name}.{name}: optional scalar is missing anyOf null"
        )
    if definition.get("default", "__MISSING__") is not None:
        violations.append(f"{entity_name}.{name}: optional scalar default is not null")
    return violations


def find_field_validation_violations(
    entity_name: str, schema: dict[str, Any]
) -> list[str]:
    """Check required/array/optional field shape consistency for one schema."""
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    violations = [
        f"{entity_name}.{name}: listed in required but missing from properties"
        for name in sorted(required)
        if name not in properties
    ]
    for name, definition in sorted(properties.items()):
        if definition.get("type") == "array":
            violations += _find_array_shape_violations(
                entity_name, name, definition, required
            )
        elif name not in required:
            violations += _find_optional_scalar_violations(
                entity_name, name, definition
            )
    return violations


def find_extracted_merged_parity_violations(
    extracted_by_name: dict[str, dict[str, Any]],
    merged_by_name: dict[str, dict[str, Any]],
) -> list[str]:
    """Check extracted and merged schemas for each entity share the same fields."""
    violations = []
    for stem in sorted(set(extracted_by_name) | set(merged_by_name)):
        if stem not in extracted_by_name:
            violations.append(f"{stem}: no extracted- schema found")
            continue
        if stem not in merged_by_name:
            violations.append(f"{stem}: no merged- schema found")
            continue
        extracted_fields = (
            set(extracted_by_name[stem]["properties"]) - EXCLUDED_PROVENANCE_FIELDS
        )
        merged_fields = set(merged_by_name[stem]["properties"]) - {"supersededBy"}
        extra_in_extracted = sorted(extracted_fields - merged_fields)
        extra_in_merged = sorted(merged_fields - extracted_fields)
        if extra_in_extracted:
            violations.append(
                f"{stem}: fields only in extracted schema: {extra_in_extracted}"
            )
        if extra_in_merged:
            violations.append(
                f"{stem}: fields only in merged schema: {extra_in_merged}"
            )
    return violations


def find_unregistered_vocabulary_violations(
    vocabulary_names: Iterable[str], concept_scheme_identifiers: set[str]
) -> list[str]:
    """Check every vocabulary file is registered in concept-schemes.json."""
    violations = []
    for name in sorted(vocabulary_names):
        identifier = f"https://mex.rki.de/item/{name.replace('_', '-')}"
        if identifier not in concept_scheme_identifiers:
            violations.append(
                f"{name}: identifier {identifier!r} not found in concept-schemes.json"
            )
    return violations


def find_duplicate_concept_id_violations(
    vocabularies_by_name: dict[str, list[dict[str, Any]]],
) -> list[str]:
    """Check that concept identifiers are unique within each vocabulary."""
    violations = []
    for name, concepts in sorted(vocabularies_by_name.items()):
        seen: set[str] = set()
        for concept in concepts:
            identifier = concept["identifier"]
            if identifier in seen:
                violations.append(f"{name}: duplicate identifier {identifier!r}")
            seen.add(identifier)
    return violations


def find_unresolved_example_violations(
    all_schemas_by_name: dict[str, dict[str, Any]],
    vocabularies_by_name: dict[str, list[dict[str, Any]]],
) -> list[str]:
    """Check that entity field examples resolve to real vocabulary concepts."""
    violations = []
    for schema_name, schema in sorted(all_schemas_by_name.items()):
        for use_scheme_node in _iter_use_scheme_nodes(schema):
            if "examples" not in use_scheme_node:
                continue
            use_scheme = str(use_scheme_node["useScheme"])
            examples = list(use_scheme_node["examples"])
            vocabulary_name = use_scheme.rsplit("/", 1)[-1].replace("-", "_")
            concepts = vocabularies_by_name.get(vocabulary_name)
            if concepts is None:
                violations.append(
                    f"{schema_name}: useScheme {use_scheme!r} has no matching "
                    "vocabulary file"
                )
                continue
            known_ids = {concept["identifier"] for concept in concepts}
            violations.extend(
                f"{schema_name}: example {example!r} not found in "
                f"vocabulary {vocabulary_name!r}"
                for example in examples
                if example not in known_ids
            )
    return violations


def find_unresolved_use_scheme_violations(
    all_schemas_by_name: dict[str, dict[str, Any]],
    vocabularies_by_name: dict[str, list[dict[str, Any]]],
) -> list[str]:
    """Check that every useScheme reference resolves to a known vocabulary.

    A vocabulary matches either by its filename-derived identifier or by the
    `inScheme` value of any of its concepts, since the two do not always
    agree.
    """
    known_schemes = {
        f"https://mex.rki.de/item/{name.replace('_', '-')}"
        for name in vocabularies_by_name
    } | {
        str(concept["inScheme"])
        for concepts in vocabularies_by_name.values()
        for concept in concepts
        if "inScheme" in concept
    }
    violations: list[str] = []
    for schema_name, schema in sorted(all_schemas_by_name.items()):
        use_schemes = {
            str(node["useScheme"]) for node in _iter_use_scheme_nodes(schema)
        }
        violations.extend(
            f"{schema_name}: useScheme {use_scheme!r} has no matching vocabulary"
            for use_scheme in sorted(use_schemes)
            if use_scheme not in known_schemes
        )
    return violations


def find_meta_schema_violations(schema_name: str, schema: dict[str, Any]) -> list[str]:
    """Check a schema document is valid against the JSON Schema 2020-12 meta-schema."""
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        return [f"{schema_name}: invalid JSON Schema document: {error.message}"]
    return []


def find_orphaned_field_violations(
    field_names: Iterable[str], all_schemas_by_name: dict[str, dict[str, Any]]
) -> list[str]:
    """Check that every shared field definition is referenced by some entity."""
    referenced = {
        ref.rsplit("/", 1)[-1]
        for schema in all_schemas_by_name.values()
        for ref in _iter_refs(schema)
        if "/mex/model/fields/" in ref
    }
    return [
        f"{name}: not referenced by any entity schema"
        for name in sorted(field_names)
        if name.replace("_", "-") not in referenced
    ]


def find_annotation_uri_violations(
    entity_name: str, schema: dict[str, Any]
) -> list[str]:
    """Check that annotation URIs on each field are well-formed and unique."""
    violations = []
    for field_name, definition in sorted(schema.get("properties", {}).items()):
        for key in ANNOTATION_URI_KEYS:
            value = definition.get(key)
            if value is None:
                continue
            uris = value if isinstance(value, list) else [value]
            seen: set[str] = set()
            for uri in uris:
                parsed = urlparse(uri)
                if not parsed.scheme or not (parsed.netloc or parsed.path):
                    violations.append(
                        f"{entity_name}.{field_name}.{key}: {uri!r} is not a "
                        "well-formed URI"
                    )
                if uri in seen:
                    violations.append(
                        f"{entity_name}.{field_name}.{key}: {uri!r} is duplicated"
                    )
                seen.add(uri)
    return violations


def find_id_path_violations(
    normalized_name: str, collection: str, schema: dict[str, Any]
) -> list[str]:
    """Check that a schema's $id (and $$target, for entities) matches its path."""
    violations = []
    file_name = normalized_name.replace("_", "-")
    expected_id = f"https://mex.rki.de/mex/model/{collection}/{file_name}"
    actual_id = schema.get("$id")
    if actual_id != expected_id:
        violations.append(
            f"{collection}/{file_name}: $id is {actual_id!r}, expected {expected_id!r}"
        )
    if "$$target" in schema:
        suffix = "#/identifier" if collection == "entities" else ""
        expected_target = f"/mex/model/{collection}/{file_name}{suffix}"
        actual_target = schema["$$target"]
        if actual_target != expected_target:
            violations.append(
                f"{collection}/{file_name}: $$target is {actual_target!r}, "
                f"expected {expected_target!r}"
            )
    return violations


def _load_concept_scheme_identifiers() -> set[str]:
    """Load the set of identifiers registered in concept-schemes.json."""
    raw = files("mex.model.vocabularies").joinpath("concept-schemes.json")
    schemes = json.loads(raw.read_text("utf-8"))
    return {scheme["identifier"] for scheme in schemes}


def _load_extension_definition() -> dict[str, Any]:
    """Load the extension/definition.json schema document."""
    raw = files("mex.model.extension").joinpath("definition.json")
    definition: dict[str, Any] = json.loads(raw.read_text("utf-8"))
    return definition


def _all_entity_schemas_by_file_stem() -> dict[str, dict[str, Any]]:
    """Combine extracted and merged schemas keyed by their actual file stem.

    `EXTRACTED_MODEL_JSON_BY_NAME` and `MERGED_MODEL_JSON_BY_NAME` both use
    the bare entity stem (e.g. "activity") with the extracted-/merged-
    prefix stripped, so naively merging them would collide; re-attach the
    prefix to get back distinct, file-matching keys.
    """
    return {
        **{
            f"extracted-{name}": schema
            for name, schema in EXTRACTED_MODEL_JSON_BY_NAME.items()
        },
        **{
            f"merged-{name}": schema
            for name, schema in MERGED_MODEL_JSON_BY_NAME.items()
        },
    }


def _collect_violations() -> list[str]:
    """Run all schema-correctness checks against the real schema files."""
    all_entities = _all_entity_schemas_by_file_stem()
    concept_scheme_identifiers = _load_concept_scheme_identifiers()

    violations: list[str] = []
    for name, schema in sorted(all_entities.items()):
        violations += find_field_validation_violations(name, schema)
        violations += find_annotation_uri_violations(name, schema)
    violations += find_extracted_merged_parity_violations(
        EXTRACTED_MODEL_JSON_BY_NAME, MERGED_MODEL_JSON_BY_NAME
    )
    violations += find_unregistered_vocabulary_violations(
        VOCABULARY_JSON_BY_NAME, concept_scheme_identifiers
    )
    violations += find_duplicate_concept_id_violations(VOCABULARY_JSON_BY_NAME)
    violations += find_unresolved_example_violations(
        all_entities, VOCABULARY_JSON_BY_NAME
    )
    violations += find_unresolved_use_scheme_violations(
        all_entities, VOCABULARY_JSON_BY_NAME
    )
    violations += find_orphaned_field_violations(FIELD_JSON_BY_NAME, all_entities)
    for name, schema in sorted(all_entities.items()):
        violations += find_meta_schema_violations(name, schema)
        violations += find_id_path_violations(name, "entities", schema)
    for name, schema in sorted(FIELD_JSON_BY_NAME.items()):
        violations += find_meta_schema_violations(f"fields/{name}", schema)
        violations += find_id_path_violations(name, "fields", schema)
    extension_definition = _load_extension_definition()
    violations += find_meta_schema_violations(
        "extension/definition", extension_definition
    )
    violations += find_id_path_violations(
        "definition", "extension", extension_definition
    )
    return violations


def main() -> int:  # pragma: no cover -- thin CLI wrapper, exercised via pre-commit
    """Run all schema-correctness checks and report the result."""
    violations = _collect_violations()
    for violation in violations:
        print(violation, file=sys.stderr)  # noqa: T201
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
