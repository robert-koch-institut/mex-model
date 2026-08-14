"""Sphinx extension rendering whole directories of json schemas.

The `jsonschema` directive renders exactly one schema file, which means every single
field and entity would have to be listed in the documentation index by hand. This module
provides a `mexschemas` directive instead, which renders all schemas of a directory that
match an optional glob pattern, sorted by filename.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from docutils import nodes
from docutils.nodes import fully_normalize_name as normalize_name
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

DEFAULT_PATTERN = "*.json"
ENCODING = "utf8"


@dataclass(frozen=True)
class Schema:
    """A json schema file together with the title it is rendered with."""

    title: str
    path: Path

    @property
    def anchor(self) -> str:
        """Return the html anchor that docutils will assign to this schema."""
        return nodes.make_id(normalize_name(self.title))

    @property
    def nav_title(self) -> str:
        """Return a condensed title for use in the navigation sidebar."""
        return self.title.replace(" ", "")


def load_schemas(directory: Path, pattern: str = DEFAULT_PATTERN) -> list[Schema]:
    """Load all schemas of the given directory matching the pattern, sorted by path."""
    return [
        Schema(
            title=str(json.loads(path.read_text("utf-8")).get("title") or path.stem),
            path=path,
        )
        for path in sorted(directory.glob(pattern))
    ]


class MExSchemasDirective(SphinxDirective):
    """Render all json schemas of a directory that match an optional glob pattern."""

    required_arguments = 1
    optional_arguments = 1
    has_content = False

    def run(self) -> list[nodes.Node]:
        """Delegate to the `jsonschema` directive for every matching schema file."""
        directory = Path(self.env.relfn2path(self.arguments[0])[1])
        pattern = self.arguments[1] if len(self.arguments) > 1 else DEFAULT_PATTERN
        lines = []
        for schema in load_schemas(directory, pattern):
            self.env.note_dependency(str(schema.path))
            lines += [
                f".. jsonschema:: {schema.path}",
                f"    :encoding: {ENCODING}",
                "",
            ]
        return self.parse_text_to_nodes("\n".join(lines))


def setup(app: Sphinx) -> dict[str, Any]:
    """Register the schemas directive."""
    app.setup_extension("sphinx-jsonschema")
    app.add_directive("mexschemas", MExSchemasDirective)
    return {"parallel_read_safe": True, "parallel_write_safe": True, "version": "1.0"}
