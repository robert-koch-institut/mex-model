"""Custom directives for embedding individual entity schemas in MyST markdown.

Provides:
    {mex-entity} EntityName   - renders extracted + merged schema tables
    {mex-field} fieldname     - renders a single field schema table
"""

from typing import Any

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective


def _jsonschema_lines(directive: SphinxDirective, path: str) -> list[str]:
    """Return `jsonschema` directive markup in the syntax of the current document.

    `parse_text_to_nodes` uses the parser of the including document, so markdown
    pages need MyST fence syntax instead of reStructuredText.
    """
    if directive.env.doc2path(directive.env.docname).suffix == ".md":
        return [f"```{{jsonschema}} {path}", ":encoding: utf8", "```", ""]
    return [f".. jsonschema:: {path}", "   :encoding: utf8", ""]


class MExEntityDirective(SphinxDirective):
    """Embed schema tables for a named entity.

    Usage in MyST markdown::

        ```{mex-entity} Resource
        :variant: both
        ```
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "variant": directives.unchanged,  # "extracted", "merged", "both", "single"
    }

    def run(self) -> list[nodes.Node]:
        entity = self.arguments[0].strip()
        variant = self.options.get("variant", "both").strip().lower()

        lines = []

        if variant in ("both", "extracted"):
            filename = f"extracted-{self._to_filename(entity)}.json"
            lines += _jsonschema_lines(self, f"../mex/model/entities/{filename}")

        if variant in ("both", "merged"):
            filename = f"merged-{self._to_filename(entity)}.json"
            lines += _jsonschema_lines(self, f"../mex/model/entities/{filename}")

        if variant == "single":
            filename = f"{self._to_filename(entity)}.json"
            lines += _jsonschema_lines(self, f"../mex/model/entities/{filename}")

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
    option_spec = {}

    def run(self) -> list[nodes.Node]:
        field = self.arguments[0].strip().lower()
        lines = _jsonschema_lines(self, f"../mex/model/fields/{field}.json")
        return self.parse_text_to_nodes("\n".join(lines))


def setup(app: Sphinx) -> dict[str, Any]:
    app.setup_extension("sphinx-jsonschema")
    app.add_directive("mex-entity", MExEntityDirective)
    app.add_directive("mex-field", MExFieldDirective)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
