"""Sphinx configuration for MEx model specification."""

import importlib
import sys
from pathlib import Path
from typing import Any

# Make the _ext directory importable
sys.path.insert(0, str(Path(__file__).parent / "_ext"))

# --- Extensions -----------------------------------------------------------

extensions = [
    "myst_parser",  # parse .md files
    "sphinx-jsonschema",  # render JSON schemas as tables
    "schemas",  # existing: .. mexschemas:: directive
    "vocabularies",  # existing: .. mexvocabularies:: directive
    "mex_schema",  # custom directives: {mex-entity}, {mex-field}
]

# --- MyST-Parser settings -------------------------------------------------

myst_enable_extensions = [
    "colon_fence",  # ::: directive syntax
    "fieldlist",  # field lists in MD
    "deflist",  # definition lists in MD
]

# Allow .md and .rst source files
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# --- Project metadata ------------------------------------------------------

project = "mex-model"

# --- HTML output settings --------------------------------------------------

html_theme = "alabaster"
html_theme_options = {
    "page_width": "100%",
    "fixed_sidebar": "true",
    "sidebar_width": "300px",
}
templates_path = ["."]

# --- sphinx-jsonschema monkey-patches (kept from original conf.py) ---------


def _patched_sphinx_jsonschema_simpletype(
    self: Any,  # noqa: ANN401 - WideFormat lives in a non-importable module
    schema: dict[str, Any],
) -> list[Any]:
    """Render the `useScheme` schema properties for every vocabulary type."""
    rows: list[Any] = _original_sphinx_jsonschema_simpletype(self, schema)
    if "useScheme" in schema:
        scheme = schema.pop("useScheme")
        rows.append(self._line(self._cell("useScheme"), self._cell(scheme)))
    return rows


def _patched_sphinx_jsonschema_kvpairs(
    self: Any,  # noqa: ANN401 - WideFormat lives in a non-importable module
    schema: dict[str, Any],
    keys: list[str],
) -> list[Any]:
    """Render `default` and `pattern` schema properties as inline code-blocks."""
    for k in keys:
        if k in schema:
            value = schema[k]
            if k in ("default", "pattern"):
                schema[k] = f"``{value}``"
    rows: list[Any] = _original_sphinx_jsonschema_kvpairs(self, schema, keys)
    return rows


sjs_wide_format = importlib.import_module("sphinx-jsonschema.wide_format")
_original_sphinx_jsonschema_simpletype = sjs_wide_format.WideFormat._simpletype
sjs_wide_format.WideFormat._simpletype = _patched_sphinx_jsonschema_simpletype
_original_sphinx_jsonschema_kvpairs = sjs_wide_format.WideFormat._kvpairs
sjs_wide_format.WideFormat._kvpairs = _patched_sphinx_jsonschema_kvpairs
