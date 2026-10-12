"""Custom directives for embedding individual entity schemas in MyST markdown.

Provides:
    {mex-entity} EntityName   - renders extracted + merged schema tables
    {mex-field} fieldname     - renders a single field schema table
"""

from pathlib import Path
from typing import Any

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective


def _jsonschema_lines(path: str) -> list[str]:
    """Return MyST markup rendering the given schema with the `jsonschema` directive.

    `parse_text_to_nodes` uses the parser of the including markdown page, so the
    directive has to be written in MyST fence syntax instead of reStructuredText.
    """
    return [f"```{{jsonschema}} {path}", ":encoding: utf8", "```", ""]


class MExEntityDirective(SphinxDirective):
    """Embed the schema tables for a named entity.

    Renders the extracted and merged variants, or the single schema of entities
    without that distinction, like `Concept`.

    Usage in MyST markdown::

        ```{mex-entity} Resource
        ```
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0

    def run(self) -> list[nodes.Node]:
        """Delegate to the `jsonschema` directive for every schema of the entity."""
        filename = self._to_filename(self.arguments[0].strip())
        paths = [
            f"../mex/model/entities/{prefix}{filename}.json"
            for prefix in ("extracted-", "merged-")
        ]
        if not Path(self.env.relfn2path(paths[0])[1]).is_file():
            paths = [f"../mex/model/entities/{filename}.json"]
        lines = [line for path in paths for line in _jsonschema_lines(path)]
        return self.parse_text_to_nodes("\n".join(lines))

    @staticmethod
    def _to_filename(entity_name: str) -> str:
        """Convert 'AccessPlatform' to 'access-platform'."""
        result = []
        for i, ch in enumerate(entity_name):
            if ch.isupper() and i > 0:
                result.append("-")
            result.append(ch.lower())
        return "".join(result)


class MExFieldDirective(SphinxDirective):
    """Embed a single field schema table.

    Usage in MyST markdown::

        ```{mex-field} identifier
        ```
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0

    def run(self) -> list[nodes.Node]:
        """Delegate to the `jsonschema` directive for the field schema."""
        field = self.arguments[0].strip().lower()
        lines = _jsonschema_lines(f"../mex/model/fields/{field}.json")
        return self.parse_text_to_nodes("\n".join(lines))


def setup(app: Sphinx) -> dict[str, Any]:
    """Register the entity and field directives."""
    app.setup_extension("sphinx-jsonschema")
    app.add_directive("mex-entity", MExEntityDirective)
    app.add_directive("mex-field", MExFieldDirective)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
