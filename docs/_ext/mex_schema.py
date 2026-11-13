"""Sphinx extension embedding individual entity and field schemas in MyST markdown.

Provides:
    {mex-entity} EntityName   - renders the extracted and merged schema tables, or the
                                single schema table of entities without that distinction
    {mex-field} fieldname     - renders a single field schema table
"""

import os
import json
from pathlib import Path
from typing import Any

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

MODEL_DIR = Path(__file__).resolve().parents[2] / "mex" / "model"
ENCODING = "utf8"


class _MExSchemaDirective(SphinxDirective):
    """Base class for directives delegating to the `jsonschema` directive."""

    has_content = False
    required_arguments = 1
    optional_arguments = 0

    def _render(self, paths: list[Path]) -> list[nodes.Node]:
        """Render the given schema files with the `jsonschema` directive.

        `parse_text_to_nodes` uses the parser of the including markdown page, so the
        directive is written in MyST fence syntax. The paths are made relative to that
        page, because `jsonschema` resolves them that way and allows no whitespace.
        """
        page_dir = self.env.doc2path(self.env.docname).parent
        lines = []
        for path in paths:
            if not path.is_file():
                msg = f"no schema found for {self.arguments[0]!r} at {path}"
                raise self.error(msg)
            lines += [
                f"```{{jsonschema}} {os.path.relpath(path, page_dir)}",
                f":encoding: {ENCODING}",
                "```",
                "",
            ]
        return self.parse_text_to_nodes("\n".join(lines))


class MExEntityDirective(_MExSchemaDirective):
    """Embed the schema tables for a named entity.

    Usage in MyST markdown::

        ```{mex-entity} Resource
        ```
    """

    def run(self) -> list[nodes.Node]:
        """Delegate to the `jsonschema` directive for every schema of the entity."""
        filename = to_filename(self.arguments[0].strip())
        entities = MODEL_DIR / "entities"
        paths = [
            entities / f"{prefix}-{filename}.json" for prefix in ("extracted", "merged")
        ]
        if not paths[0].is_file():
            paths = [entities / f"{filename}.json"]
        return self._render(paths)


class MExFieldDirective(_MExSchemaDirective):
    """Embed a single field schema table.

    Usage in MyST markdown::

        ```{mex-field} identifier
        ```
    """

    def run(self) -> list[nodes.Node]:
        """Delegate to the `jsonschema` directive for the field schema."""
        field = self.arguments[0].strip().lower()
        return self._render([MODEL_DIR / "fields" / f"{field}.json"])

class MExEntityListDirective(SphinxDirective):
    """Render an overview table of all entity schemas."""

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    def run(self) -> list[nodes.Node]:
        """Build a table from the entity schemas in the model."""
        entities_dir = MODEL_DIR / "entities"
        paths = sorted(
            path
            for path in entities_dir.glob("*.json")
            if not path.name.startswith("extracted-")
        )

        rows: list[str] = []

        for path in paths:
            self.env.note_dependency(str(path))
            schema = json.loads(path.read_text(ENCODING))

            title = str(schema.get("title") or path.stem)
            entity_name = title.removeprefix("Merged ")

            is_merged_schema = path.name.startswith("merged-")
            file_stem = path.stem.removeprefix("merged-")
            has_extracted_variant = (
                is_merged_schema
                and (entities_dir / f"extracted-{file_stem}.json").is_file()
            )
            variants = "Yes" if has_extracted_variant else "No"

            description = " ".join(
                str(schema.get("description", "")).split()
            ).replace("|", r"\|")

            rows.append(
                f"| {entity_name} | {variants} | {description} |"
            )

        lines = [
            "| Entity | Extracted/Merged | Description |",
            "| --- | --- | --- |",
            *rows,
        ]

        return self.parse_text_to_nodes("\n".join(lines))

def to_filename(entity_name: str) -> str:
    """Convert 'AccessPlatform' to 'access-platform'."""
    result = []
    for i, ch in enumerate(entity_name):
        if ch.isupper() and i > 0:
            result.append("-")
        result.append(ch.lower())
    return "".join(result)


def setup(app: Sphinx) -> dict[str, Any]:
    """Register the entity and field directives."""
    app.setup_extension("jsonschema_patches")
    app.add_directive("mex-entity", MExEntityDirective)
    app.add_directive("mex-field", MExFieldDirective)
    app.add_directive("mex-entity-list", MExEntityListDirective)
    return {"parallel_read_safe": True, "parallel_write_safe": True, "version": "1.0"}
