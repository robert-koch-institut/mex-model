"""Sphinx extension rendering example JSON instances of entities in MyST markdown.

Provides:
    {mex-example} EntityName  - renders a JSON example of the merged entity, or of the
                                extracted entity with `:variant: extracted`

The examples are generated with `mex-artificial`, which builds on the pydantic models
of `mex-common`. These models follow the released model, so every example is validated
against the local schemas and fields that do not match are dropped with a warning.
`Concept` and `ConceptScheme` examples are not generated, but shown as they are stored
in the local vocabularies. Concept identifiers in the examples are annotated with their
labels.
"""

import json
import logging
import re
from collections import defaultdict
from collections.abc import Callable
from functools import cache
from pathlib import Path
from typing import Any, ClassVar, cast

from docutils import nodes
from docutils.parsers.rst import directives
from jsonschema import Draft202012Validator
from mex_schema import MODEL_DIR, to_filename
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
from sphinx.application import Sphinx
from sphinx.util import logging as sphinx_logging
from sphinx.util.docutils import SphinxDirective

logger = sphinx_logging.getLogger(__name__)

BASE_URL = "https://mex.rki.de/"
CHATTINESS = 2
CONCEPT_SCHEMES_FILE = "concept-schemes.json"
CONCEPT_URL = re.compile(r'"(https://mex\.rki\.de/item/[-A-Za-z0-9]+)"')
CONCEPT_URL_AT_END = re.compile(CONCEPT_URL.pattern + r"\]?,?$")
ENCODING = "utf8"
IDS_PER_TYPE = 3
LINE_LENGTH = 88
MAX_ITEMS = 2
VARIANTS = ("merged", "extracted")


def schema_url(path: Path) -> str:
    """Return the `$id` of the schema stored at the given path."""
    return BASE_URL + path.relative_to(MODEL_DIR.parents[1]).with_suffix("").as_posix()


@cache
def load_registry() -> Registry[Any]:
    """Load all entity and field schemas into a registry for reference resolution.

    The model references the identifier type of an entity as `<entity>#/identifier`,
    so the identifier property is additionally exposed at the root of every schema.
    """
    resources = []
    for path in sorted(MODEL_DIR.glob("*/*.json")):
        if path.parent.name not in ("entities", "fields"):
            continue
        schema = json.loads(path.read_text(ENCODING))
        if identifier := schema.get("properties", {}).get("identifier"):
            schema = {**schema, "identifier": identifier}
        resource = Resource.from_contents(schema, default_specification=DRAFT202012)
        resources.append((schema_url(path), resource))
    return Registry().with_resources(resources)


def validate(path: Path, instance: dict[str, Any]) -> list[str]:
    """Return the top-level keys of the instance that violate the schema at `path`."""
    registry = load_registry()
    validator = Draft202012Validator(
        registry.contents(schema_url(path)), registry=registry
    )
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.json_path)
    return list(dict.fromkeys(str(e.path[0]) if e.path else "" for e in errors))


@cache
def load_vocabularies() -> dict[str, list[dict[str, Any]]]:
    """Load the concept schemes and all concepts from the local vocabularies."""
    vocabularies = MODEL_DIR / "vocabularies"
    concepts = [
        concept
        for path in sorted(vocabularies.glob("*.json"))
        if path.name != CONCEPT_SCHEMES_FILE
        for concept in json.loads(path.read_text(ENCODING))
    ]
    schemes = json.loads((vocabularies / CONCEPT_SCHEMES_FILE).read_text(ENCODING))
    return {"Concept": concepts, "ConceptScheme": schemes}


@cache
def load_labels() -> dict[str, str]:
    """Return the english label of every concept by its identifier."""
    return {
        concept["identifier"]: concept["prefLabel"].get("en", "")
        for concept in load_vocabularies()["Concept"]
    }


def _simplify(value: Any) -> Any:  # noqa: ANN401
    """Remove empty values and the `entityType` discriminator and shorten lists."""
    if isinstance(value, dict):
        return {
            k: _simplify(v)
            for k, v in value.items()
            if v not in (None, []) and k != "entityType"
        }
    if isinstance(value, list):
        return [_simplify(v) for v in value[:MAX_ITEMS]]
    return value


class UnsupportedEntityError(LookupError):
    """Raised when the installed `mex-common` has no model for an entity yet."""


def generate_artificial(entity_name: str, variant: str, seed: int) -> dict[str, Any]:
    """Generate an artificial extracted or merged item with `mex-artificial`.

    Raises:
        UnsupportedEntityError: If `mex-common` does not implement the entity yet.
    """
    # imported lazily, because they are only available with the `docs` dependencies
    from mex.artificial.helpers import create_faker  # noqa: PLC0415
    from mex.common.merged.main import create_merged_item  # noqa: PLC0415
    from mex.common.models import (  # noqa: PLC0415
        EXTRACTED_MODEL_CLASSES,
        EXTRACTED_MODEL_CLASSES_BY_NAME,
    )
    from mex.common.transform import MExEncoder  # noqa: PLC0415
    from mex.common.types import Identifier, Validation  # noqa: PLC0415

    if f"Extracted{entity_name}" not in EXTRACTED_MODEL_CLASSES_BY_NAME:
        raise UnsupportedEntityError(entity_name)

    # silence the settings table that mex-common logs when it is first loaded
    logging.getLogger("mex").setLevel(logging.WARNING)

    # provide some merged identifiers for every type, so references can be filled
    ids_by_type = defaultdict(
        list,
        {
            model.stemType: [
                Identifier.generate(seed=type_index * IDS_PER_TYPE + id_index)
                for id_index in range(IDS_PER_TYPE)
            ]
            for type_index, model in enumerate(EXTRACTED_MODEL_CLASSES)
        },
    )
    faker = create_faker(seed=seed, chattiness=CHATTINESS)
    item = faker.extracted_item([entity_name], ids_by_type)
    if variant == "merged":
        item = create_merged_item(
            item.stableTargetId, [item], None, validation=Validation.IGNORE
        )
    return cast(
        "dict[str, Any]", _simplify(json.loads(json.dumps(item, cls=MExEncoder)))
    )


def find_concept(entity_name: str, identifier: str | None) -> dict[str, Any]:
    """Return the concept or concept scheme with the given identifier, or the first."""
    for concept in load_vocabularies()[entity_name]:
        if identifier in (None, concept["identifier"]):
            return concept
    msg = f"no {entity_name} found with identifier {identifier!r}"
    raise ValueError(msg)


def _format(value: Any, indent: int = 0, column: int = 0) -> str:  # noqa: ANN401
    """Dump the value as JSON, keeping it on one line where it fits.

    `indent` is the indentation of the line the value is on and `column` is where the
    value starts on that line. Lists with more than one concept are always split up,
    so that every concept identifier ends a line and can be annotated with its label.
    """
    inline = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if not value or not isinstance(value, dict | list):
        return inline
    concepts = CONCEPT_URL.findall(inline) if isinstance(value, list) else []
    if column + len(inline) <= LINE_LENGTH and len(concepts) < 2:  # noqa: PLR2004
        return inline
    pad = " " * (indent + 2)
    if isinstance(value, dict):
        items = [
            f"{pad}{json.dumps(k)}: "
            + _format(v, indent + 2, indent + 2 + len(json.dumps(k)) + 2)
            for k, v in sorted(value.items())
        ]
        brackets = "{}"
    else:
        items = [f"{pad}{_format(v, indent + 2, indent + 2)}" for v in value]
        brackets = "[]"
    return f"{brackets[0]}\n" + ",\n".join(items) + f"\n{' ' * indent}{brackets[1]}"


def to_json(instance: dict[str, Any]) -> str:
    """Dump the instance as JSON and annotate referenced concepts with their labels."""
    labels = load_labels()
    lines = []
    for line in _format(instance).splitlines():
        if (
            not line.lstrip().startswith('"identifier"')
            and (match := CONCEPT_URL_AT_END.search(line))
            and (label := labels.get(match[1]))
        ):
            line = f"{line}  // {label}"  # noqa: PLW2901
        lines.append(line)
    return "\n".join(lines)


def to_variant(argument: str) -> str:
    """Convert the `:variant:` option and ensure it is valid."""
    return directives.choice(argument, VARIANTS)


class MExExampleDirective(SphinxDirective):
    """Embed an example JSON instance of a named entity.

    Usage in MyST markdown::

        ```{mex-example} Resource
        :variant: extracted
        :seed: 1
        ```
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec: ClassVar[dict[str, Callable[[str], Any]]] = {
        "variant": to_variant,
        "seed": directives.nonnegative_int,
        "identifier": directives.unchanged_required,
    }

    def run(self) -> list[nodes.Node]:
        """Generate, validate and render the example as a JSON literal block."""
        entity_name = self.arguments[0].strip()
        if entity_name in ("Concept", "ConceptScheme"):
            try:
                concept = find_concept(entity_name, self.options.get("identifier"))
            except ValueError as error:
                raise self.error(str(error)) from error
            return self._render(concept)
        variant = self.options.get("variant", "merged")
        path = MODEL_DIR / "entities" / f"{variant}-{to_filename(entity_name)}.json"
        if not path.is_file():
            msg = f"no schema found for {entity_name!r} at {path}"
            raise self.error(msg)
        try:
            instance = generate_artificial(
                entity_name, variant, self.options.get("seed", 0)
            )
        except ImportError:
            self._warn(
                "cannot generate example for %r, install the `docs` group", entity_name
            )
            return []
        except UnsupportedEntityError:
            # not a warning, so the docs keep building until mex-common catches up
            logger.info(
                "no example for %r, it is not supported by mex-common yet",
                entity_name,
                location=self.get_location(),
            )
            note = nodes.note()
            note += nodes.paragraph(
                text=(
                    f"An example for {entity_name} will be generated here, once it is "
                    "supported by mex-common."
                )
            )
            self.set_source_info(note)
            return [note]
        if invalid := validate(path, instance):
            self._warn(
                "example for %r violates %s at %s, dropping these fields",
                entity_name,
                path.name,
                ", ".join(repr(key) for key in invalid),
            )
            instance = {k: v for k, v in instance.items() if k not in invalid}
        return self._render(instance)

    def _warn(self, msg: str, *args: object) -> None:
        """Log a warning for this directive that can be suppressed as `mex.example`."""
        logger.warning(
            msg, *args, location=self.get_location(), type="mex", subtype="example"
        )

    def _render(self, instance: dict[str, Any]) -> list[nodes.Node]:
        """Render the given instance as a JSON literal block."""
        text = to_json(instance)
        block = nodes.literal_block(text, text, language="json")
        self.set_source_info(block)
        return [block]


def setup(app: Sphinx) -> dict[str, Any]:
    """Register the example directive."""
    app.add_directive("mex-example", MExExampleDirective)
    return {"parallel_read_safe": True, "parallel_write_safe": True, "version": "1.0"}
