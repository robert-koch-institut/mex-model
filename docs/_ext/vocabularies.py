"""Sphinx extension rendering the MEx vocabularies as tables.

The vocabularies are not JSON schemas but plain arrays of concepts, so they cannot be
rendered with the `jsonschema` directive that is used for entities and fields. This
module provides a `mexvocabularies` directive instead, which renders one section with
one concept table per vocabulary and registers the concept scheme identifiers as labels,
so that the `useScheme` properties of the entities can link to them.
"""

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from docutils import nodes, statemachine
from docutils.nodes import fully_normalize_name as normalize_name
from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

logger = logging.getLogger(__name__)

CONCEPT_SCHEMES_FILE = "concept-schemes.json"
ESCAPE_PATTERN = re.compile(r"([\\*`_|])")
ITEM_URL = "https://mex.rki.de/item/"
TITLE_SUFFIX = " vocabulary"

Cell = tuple[int, int, int, statemachine.StringList]


@dataclass(frozen=True)
class Vocabulary:
    """A concept scheme together with the concepts that belong to it."""

    identifier: str
    scheme_identifier: str
    title: str
    description: str
    concepts: list[dict[str, Any]]
    path: Path

    @property
    def identifiers(self) -> set[str]:
        """Return all identifiers this vocabulary should be linkable by."""
        return {self.identifier, self.scheme_identifier}

    @property
    def anchor(self) -> str:
        """Return the html anchor that docutils will assign to this vocabulary."""
        return nodes.make_id(normalize_name(self.title))

    @property
    def nav_title(self) -> str:
        """Return a shortened title for use in the navigation sidebar."""
        return self.title.removesuffix(TITLE_SUFFIX) or self.title


def _localized(value: Any, language: str = "en") -> str:  # noqa: ANN401
    """Return the text of the given language from a possibly localized value."""
    if isinstance(value, dict):
        return str(value.get(language) or next(iter(value.values()), ""))
    return str(value or "")


def _title_from_path(path: Path) -> str:
    """Derive a human-readable scheme title from a vocabulary filename."""
    return f"{path.stem.replace('-', ' ').capitalize()}{TITLE_SUFFIX}"


def _concept_sort_key(concept: dict[str, Any]) -> tuple[int, str]:
    """Sort concepts by the numeric suffix of their identifier."""
    identifier = str(concept.get("identifier", ""))
    suffix = identifier.rpartition("-")[2]
    return (int(suffix) if suffix.isdigit() else sys.maxsize, identifier)


def load_vocabularies(directory: Path) -> list[Vocabulary]:
    """Load all vocabularies of the given directory, sorted by title."""
    schemes = {
        str(scheme["identifier"]): scheme
        for scheme in json.loads((directory / CONCEPT_SCHEMES_FILE).read_text("utf-8"))
    }
    vocabularies = []
    for path in sorted(directory.glob("*.json")):
        if path.name == CONCEPT_SCHEMES_FILE:
            continue
        concepts = sorted(json.loads(path.read_text("utf-8")), key=_concept_sort_key)
        if not concepts:
            continue
        identifier = f"{ITEM_URL}{path.stem}"
        scheme_identifier = str(concepts[0].get("inScheme") or identifier)
        scheme = schemes.get(scheme_identifier) or schemes.get(identifier) or {}
        vocabularies.append(
            Vocabulary(
                identifier=identifier,
                scheme_identifier=scheme_identifier,
                title=str(scheme.get("label") or _title_from_path(path)),
                description=_localized(scheme.get("description")),
                concepts=concepts,
                path=path,
            )
        )
    return sorted(vocabularies, key=lambda vocabulary: vocabulary.title)


class MExVocabulariesDirective(SphinxDirective):
    """Render all vocabularies of a directory as a section with a table each."""

    required_arguments = 1
    has_content = False

    columns: ClassVar[list[str]] = ["Label", "Identifier", "Definition"]
    column_widths: ClassVar[list[int]] = [20, 30, 50]

    def run(self) -> list[nodes.Node]:
        """Build one section with a concept table for each vocabulary."""
        directory = Path(self.env.relfn2path(self.arguments[0])[1])
        self.env.note_dependency(str(directory / CONCEPT_SCHEMES_FILE))
        sections: list[nodes.Node] = []
        for vocabulary in load_vocabularies(directory):
            self.env.note_dependency(str(vocabulary.path))
            if vocabulary.scheme_identifier != vocabulary.identifier:
                logger.warning(
                    "inScheme %s of %s does not match its filename, "
                    "registering both spellings",
                    vocabulary.scheme_identifier,
                    vocabulary.path.name,
                    location=(self.env.docname, self.lineno),
                )
            sections.append(self._section(vocabulary))
        return sections

    def _section(self, vocabulary: Vocabulary) -> nodes.section:
        """Build a section holding the description and table of one vocabulary."""
        section = nodes.section()
        section["names"].append(normalize_name(vocabulary.title))
        section += nodes.title(vocabulary.title, "", nodes.Text(vocabulary.title))
        self.state.document.note_implicit_target(section, section)
        self._register_label(vocabulary, section)
        if vocabulary.description:
            section += nodes.paragraph(text=vocabulary.description)
        section += self._table(vocabulary)
        return section

    def _register_label(self, vocabulary: Vocabulary, section: nodes.section) -> None:
        """Register the scheme identifiers as labels, so `useScheme` can link here."""
        anchor = section["ids"][0]
        labels = self.env.domaindata["std"]["labels"]
        anonlabels = self.env.domaindata["std"]["anonlabels"]
        for identifier in vocabulary.identifiers:
            name = normalize_name(identifier)
            labels[name] = (self.env.docname, anchor, vocabulary.title)
            anonlabels[name] = (self.env.docname, anchor)

    def _table(self, vocabulary: Vocabulary) -> nodes.table:
        """Build a table listing all concepts of one vocabulary."""
        head = [[self._cell(column) for column in self.columns]]
        body = [
            [
                self._cell(_localized(concept.get("prefLabel"))),
                self._cell(f"``{concept['identifier']}``", escape=False),
                self._cell(_localized(concept.get("definition"))),
            ]
            for concept in vocabulary.concepts
        ]
        return self.state.build_table((self.column_widths, head, body), self.lineno)

    def _cell(self, text: str, *, escape: bool = True) -> Cell:
        """Convert a string into a cell as expected by the docutils table builder."""
        if escape:
            text = ESCAPE_PATTERN.sub(r"\\\1", text)
        lines = statemachine.string2lines(text)
        source = self.state.document.current_source
        items = [(source, self.lineno)] * len(lines)
        return (0, 0, self.lineno, statemachine.StringList(lines, items=items))


def setup(app: Sphinx) -> dict[str, Any]:
    """Register the vocabularies directive."""
    app.add_directive("mexvocabularies", MExVocabulariesDirective)
    return {"parallel_read_safe": True, "parallel_write_safe": True, "version": "1.0"}
