"""Sphinx extension rendering example JSON instances of entities in MyST markdown.

Provides:
    {mex-example} EntityName  - renders a JSON example of the merged entity

The examples are generated with `mex-artificial`, which builds on the pydantic models
of `mex-common`. `Concept` and `ConceptScheme` examples are not generated, but shown as
they are stored in the local vocabularies. Concept identifiers in the examples are
annotated with their labels.
"""

import json
import logging
import re
from collections import defaultdict
from collections.abc import Callable
from functools import cache
from importlib.metadata import version
from typing import Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from mex_schema import MODEL_DIR, to_filename
from sphinx.application import Sphinx
from sphinx.util import logging as sphinx_logging
from sphinx.util.docutils import SphinxDirective

from mex.artificial.helpers import create_faker
from mex.common.merged.main import create_merged_item
from mex.common.models import EXTRACTED_MODEL_CLASSES, EXTRACTED_MODEL_CLASSES_BY_NAME
from mex.common.types import Identifier, Validation

logger = sphinx_logging.getLogger(__name__)

CHATTINESS = 2
CONCEPT_SCHEMES_FILE = "concept-schemes.json"
CONCEPT_URL_AT_END = re.compile(r'"(https://mex\.rki\.de/item/[-A-Za-z0-9]+)",?$')
ENCODING = "utf8"
IDS_PER_TYPE = 3
SEED = 0


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


class UnsupportedEntityError(LookupError):
    """Raised when the installed `mex-common` has no model for an entity yet."""


def generate_artificial(entity_name: str) -> dict[str, Any]:
    """Generate an artificial merged item with `mex-artificial`.

    Raises:
        UnsupportedEntityError: If `mex-common` does not implement the entity yet.
    """
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
    faker = create_faker(seed=SEED, chattiness=CHATTINESS)
    extracted = faker.extracted_item([entity_name], ids_by_type)
    merged = create_merged_item(
        extracted.stableTargetId, [extracted], None, validation=Validation.STRICT
    )
    return merged.model_dump(mode="json", exclude={"entityType"}, exclude_none=True)


def find_concept(entity_name: str, identifier: str) -> dict[str, Any]:
    """Return the concept or concept scheme with the given identifier."""
    for concept in load_vocabularies()[entity_name]:
        if concept["identifier"] == identifier:
            return concept
    msg = f"no {entity_name} found with identifier {identifier!r}"
    raise ValueError(msg)


def to_json(instance: dict[str, Any]) -> str:
    """Dump the instance as JSON and annotate referenced concepts with their labels."""
    labels = load_labels()
    lines = []
    for line in json.dumps(
        instance, indent=2, sort_keys=True, ensure_ascii=False
    ).splitlines():
        if (
            not line.lstrip().startswith('"identifier"')
            and (match := CONCEPT_URL_AT_END.search(line))
            and (label := labels.get(match[1]))
        ):
            line = f"{line}  // {label}"  # noqa: PLW2901
        lines.append(line)
    return "\n".join(lines)


class MExExampleDirective(SphinxDirective):
    """Embed an example JSON instance of a named entity.

    Usage in MyST markdown::

        ```{mex-example} Resource
        ```

        ```{mex-example} Concept
        :identifier: https://mex.rki.de/item/health-category-16
        ```
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec: ClassVar[dict[str, Callable[[str], Any]]] = {
        "identifier": directives.unchanged_required,
    }

    def run(self) -> list[nodes.Node]:
        """Generate and render the example as a JSON literal block."""
        entity_name = self.arguments[0].strip()
        if entity_name in ("Concept", "ConceptScheme"):
            if "identifier" not in self.options:
                msg = f"{entity_name} examples require an :identifier: option"
                raise self.error(msg)
            try:
                concept = find_concept(entity_name, self.options["identifier"])
            except ValueError as error:
                raise self.error(str(error)) from error
            return self._render(to_json(concept))
        path = MODEL_DIR / "entities" / f"merged-{to_filename(entity_name)}.json"
        if not path.is_file():
            msg = f"no schema found for {entity_name!r} at {path}"
            raise self.error(msg)
        try:
            instance = generate_artificial(entity_name)
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
        generator = f"mex-artificial=={version('mex-artificial')}"
        header = f"// autogenerated example using {generator}"
        return self._render(f"{header}\n{to_json(instance)}")

    def _render(self, text: str) -> list[nodes.Node]:
        """Render the given text as a JSON literal block."""
        block = nodes.literal_block(text, text, language="json")
        self.set_source_info(block)
        return [block]


def setup(app: Sphinx) -> dict[str, Any]:
    """Register the example directive."""
    app.add_directive("mex-example", MExExampleDirective)
    return {"parallel_read_safe": True, "parallel_write_safe": True, "version": "1.0"}
