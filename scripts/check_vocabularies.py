"""Standalone correctness checks for the mex-model vocabularies.

Run directly (`uv run python scripts/check_vocabularies.py`) or via the
`vocabulary-checks` pre-commit hook. The same `find_*_violations` functions are
imported by the test suite for both real-data regression tests and
fixture-based self-tests.

Covers the vocabulary files themselves (validity against `concept.json`, scheme
membership, duplicates; shared `exactMatch` targets only warn), the
`concept-schemes.json` registry (validity against
`concept-scheme.json`, both-way registration), and entity references into the
vocabularies (`useScheme`, `examples`).
"""

import json
import sys
from collections.abc import Iterable, Iterator
from copy import deepcopy
from importlib.resources import files
from typing import Any
from urllib.parse import urlparse

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from mex.model import (
    EXTRACTED_MODEL_JSON_BY_NAME,
    MERGED_MODEL_JSON_BY_NAME,
    VOCABULARY_JSON_BY_NAME,
)

ANNOTATION_URI_KEYS = ("closeMatch", "exactMatch", "sameAs", "subPropertyOf")
ITEM_PREFIX = "https://mex.rki.de/item/"
PREF_LABEL_LANGUAGES = ("de", "en")


def _scheme_identifier(vocabulary_name: str) -> str:
    """Return the concept scheme identifier derived from a vocabulary name."""
    return f"{ITEM_PREFIX}{vocabulary_name.replace('_', '-')}"


def _as_list(value: object) -> list[object]:
    """Wrap a scalar in a list, pass lists through and turn `None` into `[]`."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


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


def _with_identifier_pointer(schema: dict[str, Any]) -> dict[str, Any]:
    """Add a top-level `identifier` key mirroring `properties.identifier`.

    Schemas reference each other as `<id>#/identifier`, which only resolves as
    a standard JSON Pointer if `identifier` exists at the document root.
    """
    patched = deepcopy(schema)
    patched["identifier"] = patched["properties"]["identifier"]
    return patched


def build_validators(
    concept_schema: dict[str, Any], concept_scheme_schema: dict[str, Any]
) -> tuple[Draft202012Validator, Draft202012Validator]:
    """Build validators for concepts and concept schemes that resolve each other."""
    schemas = [_with_identifier_pointer(concept_schema)]
    schemas.append(_with_identifier_pointer(concept_scheme_schema))
    registry: Registry[Any] = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema, DRAFT202012))
        for schema in schemas
    )
    concept_validator, scheme_validator = (
        Draft202012Validator(schema, registry=registry) for schema in schemas
    )
    return concept_validator, scheme_validator


def _schema_errors(
    location: str, validator: Draft202012Validator, instance: object
) -> Iterator[str]:
    """Yield one readable, deterministically ordered message per schema error."""
    messages = set()
    for error in validator.iter_errors(instance):
        path = ".".join(str(part) for part in error.absolute_path)
        messages.add(f"{location}{'.' + path if path else ''}: {error.message}")
    yield from sorted(messages)


def find_concept_schema_violations(
    vocabularies_by_name: dict[str, list[dict[str, Any]]],
    concept_validator: Draft202012Validator,
) -> list[str]:
    """Check that every concept of every vocabulary is valid against concept.json."""
    violations: list[str] = []
    for name, concepts in sorted(vocabularies_by_name.items()):
        for concept in concepts:
            location = f"{name}.{concept.get('identifier', '<no identifier>')}"
            violations.extend(_schema_errors(location, concept_validator, concept))
    return violations


def find_concept_scheme_schema_violations(
    concept_schemes: list[dict[str, Any]], scheme_validator: Draft202012Validator
) -> list[str]:
    """Check that every registered scheme is valid against concept-scheme.json."""
    violations: list[str] = []
    for scheme in concept_schemes:
        location = f"concept-schemes.{scheme.get('identifier', '<no identifier>')}"
        violations.extend(_schema_errors(location, scheme_validator, scheme))
    return violations


def find_duplicate_concept_scheme_violations(
    concept_schemes: list[dict[str, Any]],
) -> list[str]:
    """Check that every scheme is registered only once in concept-schemes.json."""
    seen: set[str] = set()
    violations = []
    for scheme in concept_schemes:
        identifier = str(scheme.get("identifier"))
        if identifier in seen:
            violations.append(f"concept-schemes: duplicate identifier {identifier!r}")
        seen.add(identifier)
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


def find_unbacked_concept_scheme_violations(
    vocabulary_names: Iterable[str], concept_scheme_identifiers: set[str]
) -> list[str]:
    """Check every scheme in concept-schemes.json has a vocabulary file."""
    known = {_scheme_identifier(name) for name in vocabulary_names}
    return [
        f"concept-schemes: {identifier!r} has no vocabulary file"
        for identifier in sorted(concept_scheme_identifiers - known)
    ]


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


def find_scheme_membership_violations(
    vocabularies_by_name: dict[str, list[dict[str, Any]]],
) -> list[str]:
    """Check each concept belongs to the scheme of the file it is listed in.

    Both `inScheme` and the identifier prefix must match the scheme identifier
    derived from the vocabulary file name.
    """
    violations = []
    for name, concepts in sorted(vocabularies_by_name.items()):
        expected = _scheme_identifier(name)
        for concept in concepts:
            identifier = str(concept.get("identifier"))
            in_scheme = concept.get("inScheme")
            if in_scheme is not None and in_scheme != expected:
                violations.append(
                    f"{name}.{identifier}: inScheme is {in_scheme!r}, "
                    f"expected {expected!r}"
                )
            if not identifier.startswith(f"{expected}-"):
                violations.append(
                    f"{name}.{identifier}: identifier does not start with "
                    f"{expected + '-'!r}"
                )
    return violations


def find_unresolved_broader_violations(
    vocabularies_by_name: dict[str, list[dict[str, Any]]],
) -> list[str]:
    """Check every `broader` reference points at a concept of the same vocabulary."""
    violations: list[str] = []
    for name, concepts in sorted(vocabularies_by_name.items()):
        known_ids = {concept.get("identifier") for concept in concepts}
        for concept in concepts:
            violations.extend(
                f"{name}.{concept.get('identifier')}: broader {broader!r} not found "
                f"in vocabulary {name!r}"
                for broader in _as_list(concept.get("broader"))
                if broader not in known_ids
            )
    return violations


def find_duplicate_pref_label_violations(
    vocabularies_by_name: dict[str, list[dict[str, Any]]],
) -> list[str]:
    """Check that no two concepts of a vocabulary share a prefLabel in a language."""
    violations: list[str] = []
    for name, concepts in sorted(vocabularies_by_name.items()):
        for language in PREF_LABEL_LANGUAGES:
            ids_by_label: dict[str, list[str]] = {}
            for concept in concepts:
                pref_label = concept.get("prefLabel")
                if isinstance(pref_label, dict) and language in pref_label:
                    ids_by_label.setdefault(str(pref_label[language]), []).append(
                        str(concept.get("identifier"))
                    )
            violations.extend(
                f"{name}: prefLabel.{language} {label!r} is used by {identifiers}"
                for label, identifiers in sorted(ids_by_label.items())
                if len(identifiers) > 1
            )
    return violations


def find_shared_exact_match_warnings(
    vocabularies_by_name: dict[str, list[dict[str, Any]]],
) -> list[str]:
    """Warn when two concepts of a vocabulary share an exactMatch target.

    SKOS `exactMatch` is transitive, so a shared target declares the concepts
    equivalent. That is usually a `closeMatch` or `broadMatch` in disguise, but
    not always wrong, so it is reported without failing the check.
    """
    warnings: list[str] = []
    for name, concepts in sorted(vocabularies_by_name.items()):
        ids_by_uri: dict[str, list[str]] = {}
        for concept in concepts:
            for uri in _as_list(concept.get("exactMatch")):
                ids_by_uri.setdefault(str(uri), []).append(
                    str(concept.get("identifier"))
                )
        warnings.extend(
            f"{name}: exactMatch {uri!r} is shared by {identifiers}"
            for uri, identifiers in sorted(ids_by_uri.items())
            if len(identifiers) > 1
        )
    return warnings


def uri_list_violations(location: str, value: object) -> list[str]:
    """Check that an annotation is an array of well-formed, unique URIs.

    `extension/definition.json` declares `closeMatch` and `exactMatch` as arrays,
    so a bare string is flagged, but its URI is still checked for well-formedness.
    """
    violations = []
    if isinstance(value, list):
        uris = [str(uri) for uri in value]
    else:
        violations.append(f"{location}: {value!r} is not an array")
        uris = [str(value)]
    seen: set[str] = set()
    for uri in uris:
        parsed = urlparse(uri)
        if not parsed.scheme or not (parsed.netloc or parsed.path):
            violations.append(f"{location}: {uri!r} is not a well-formed URI")
        if uri in seen:
            violations.append(f"{location}: {uri!r} is duplicated")
        seen.add(uri)
    return violations


def find_concept_annotation_violations(
    vocabularies_by_name: dict[str, list[dict[str, Any]]],
) -> list[str]:
    """Check that annotation URIs on each concept are well-formed, unique arrays."""
    violations = []
    for name, concepts in sorted(vocabularies_by_name.items()):
        for concept in concepts:
            for key in ANNOTATION_URI_KEYS:
                if key in concept:
                    violations += uri_list_violations(
                        f"{name}.{concept['identifier']}.{key}", concept[key]
                    )
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


def _load_json(package: str, file_name: str) -> Any:  # noqa: ANN401
    """Load one json file shipped inside a `mex.model` subpackage."""
    return json.loads(files(package).joinpath(file_name).read_text("utf-8"))


def entity_schemas_by_file_stem() -> dict[str, dict[str, Any]]:
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
    """Run all vocabulary checks against the real vocabulary and schema files."""
    concept_schemes: list[dict[str, Any]] = _load_json(
        "mex.model.vocabularies", "concept-schemes.json"
    )
    concept_scheme_identifiers = {
        str(scheme.get("identifier")) for scheme in concept_schemes
    }
    concept_validator, scheme_validator = build_validators(
        _load_json("mex.model.entities", "concept.json"),
        _load_json("mex.model.entities", "concept-scheme.json"),
    )
    all_entities = entity_schemas_by_file_stem()

    violations = find_concept_schema_violations(
        VOCABULARY_JSON_BY_NAME, concept_validator
    )
    violations += find_concept_scheme_schema_violations(
        concept_schemes, scheme_validator
    )
    violations += find_duplicate_concept_scheme_violations(concept_schemes)
    violations += find_unregistered_vocabulary_violations(
        VOCABULARY_JSON_BY_NAME, concept_scheme_identifiers
    )
    violations += find_unbacked_concept_scheme_violations(
        VOCABULARY_JSON_BY_NAME, concept_scheme_identifiers
    )
    violations += find_duplicate_concept_id_violations(VOCABULARY_JSON_BY_NAME)
    violations += find_scheme_membership_violations(VOCABULARY_JSON_BY_NAME)
    violations += find_unresolved_broader_violations(VOCABULARY_JSON_BY_NAME)
    violations += find_duplicate_pref_label_violations(VOCABULARY_JSON_BY_NAME)
    violations += find_concept_annotation_violations(VOCABULARY_JSON_BY_NAME)
    violations += find_unresolved_example_violations(
        all_entities, VOCABULARY_JSON_BY_NAME
    )
    violations += find_unresolved_use_scheme_violations(
        all_entities, VOCABULARY_JSON_BY_NAME
    )
    return violations


def _collect_warnings() -> list[str]:
    """Run all advisory vocabulary checks, which report but never fail."""
    return find_shared_exact_match_warnings(VOCABULARY_JSON_BY_NAME)


def main() -> int:  # pragma: no cover
    """Run all vocabulary checks, report warnings, and fail only on violations."""
    for warning in _collect_warnings():
        print(f"warning: {warning}", file=sys.stderr)  # noqa: T201
    violations = _collect_violations()
    for violation in violations:
        print(violation, file=sys.stderr)  # noqa: T201
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
