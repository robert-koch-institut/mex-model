"""Custom directives for embedding individual entity schemas in MyST markdown.

Provides:
    {mex-entity} EntityName   - renders extracted + merged schema tables
    {mex-field} fieldname     - renders a single field schema table
"""

from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective


class MexEntityDirective(SphinxDirective):
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

    def run(self):
        entity = self.arguments[0].strip()
        variant = self.options.get("variant", "both").strip().lower()

        lines = []

        if variant in ("both", "extracted"):
            filename = f"extracted-{self._to_filename(entity)}.json"
            lines.append(f".. jsonschema:: ../mex/model/entities/{filename}")
            lines.append("   :encoding: utf8")
            lines.append("")

        if variant in ("both", "merged"):
            filename = f"merged-{self._to_filename(entity)}.json"
            lines.append(f".. jsonschema:: ../mex/model/entities/{filename}")
            lines.append("   :encoding: utf8")
            lines.append("")

        if variant == "single":
            filename = f"{self._to_filename(entity)}.json"
            lines.append(f".. jsonschema:: ../mex/model/entities/{filename}")
            lines.append("   :encoding: utf8")
            lines.append("")

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


class MexFieldDirective(SphinxDirective):
    """Embed a single field schema table.

    Usage in MyST markdown::

        ```{mex-field} identifier
        ```
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {}

    def run(self):
        field = self.arguments[0].strip().lower()
        lines = [
            f".. jsonschema:: ../mex/model/fields/{field}.json",
            "   :encoding: utf8",
            "",
        ]
        return self.parse_text_to_nodes("\n".join(lines))


def setup(app):
    app.setup_extension("sphinx-jsonschema")
    app.add_directive("mex-entity", MexEntityDirective)
    app.add_directive("mex-field", MexFieldDirective)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
