"""Helper building the sidebar navigation from the documentation index.

The alabaster theme has no support for a table of contents within a single document, so
the sidebar links have to be configured manually as `extra_nav_links`. Instead of
maintaining that list by hand, this module parses the sections and directives of the
index file and derives one link per section, per rendered json schema and per rendered
vocabulary, in the order in which they appear in the document. The schemas and
vocabularies are resolved exactly like the directives that render them do, so that the
sidebar cannot drift apart from the document body.
"""

import re
from pathlib import Path

from docutils import nodes
from docutils.nodes import fully_normalize_name as normalize_name
from schemas import DEFAULT_PATTERN, load_schemas
from vocabularies import load_vocabularies

BULLETS = ("", "• ", "◦ ")
DIRECTIVE_PATTERN = re.compile(r"^\.\.\s+(mexschemas|mexvocabularies)::\s+(.+?)\s*$")
UNDERLINE_PATTERN = re.compile(r"""^([=\-^"'~*+#`:.,_])\1+$""")


def _anchor(title: str) -> str:
    """Return the html anchor that docutils will assign to the given title."""
    return nodes.make_id(normalize_name(title))


def _label(depth: int, title: str) -> str:
    """Return the sidebar label for a title on the given nesting depth."""
    return f"{BULLETS[min(depth, len(BULLETS) - 1)]}{title}"


def build_nav_links(index: Path) -> dict[str, str]:
    """Build a mapping of sidebar labels to anchors for the given index file.

    Sections are listed with their own title, json schemas with their title stripped of
    spaces and vocabularies with their shortened scheme title. The nesting depth of an
    entry determines the bullet it is prefixed with, whereas the document title itself
    is skipped, because it is already linked by the theme's logo.

    Args:
        index: Path to the reStructuredText file that contains the documentation

    Returns:
        Mapping of sidebar labels to the anchors of the sections they link to
    """
    lines = index.read_text("utf-8").splitlines()
    links: dict[str, str] = {}
    styles: list[str] = []
    depth = 0
    for number, line in enumerate(lines):
        title = line.strip()
        underline = lines[number + 1].strip() if number + 1 < len(lines) else ""
        is_section = UNDERLINE_PATTERN.match(underline) and len(underline) >= len(title)
        if title and is_section:
            if underline[0] not in styles:
                styles.append(underline[0])
            depth = styles.index(underline[0])
            if depth:
                links[_label(depth - 1, title)] = f"#{_anchor(title)}"
        elif match := DIRECTIVE_PATTERN.match(line):
            directive, arguments = match.groups()
            argument, _, pattern = arguments.partition(" ")
            path = (index.parent / argument).resolve()
            if directive == "mexschemas":
                for schema in load_schemas(path, pattern.strip() or DEFAULT_PATTERN):
                    links[_label(depth, schema.nav_title)] = f"#{schema.anchor}"
            else:
                for vocabulary in load_vocabularies(path):
                    links[_label(depth, vocabulary.nav_title)] = f"#{vocabulary.anchor}"
    return links
