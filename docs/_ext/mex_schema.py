"""Sphinx extension embedding individual entity and field schemas in MyST markdown.

Provides:
    {mex-entity} EntityName   - renders the extracted and merged schema tables, or the
                                single schema table of entities without that distinction
    {mex-field} fieldname     - renders a single field schema table
"""

import os
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
    return {"parallel_read_safe": True, "parallel_write_safe": True, "version": "1.0"}
