# sphinx configuration

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from navigation import build_nav_links

extensions = ["sphinx-jsonschema", "schemas", "vocabularies"]
html_theme = "alabaster"
html_theme_options = {
    "extra_nav_links": build_nav_links(Path(__file__).parent / "index.rst"),
    "page_width": "80%",
    "body_max_width": "100%",
    "fixed_sidebar": "true",
    "sidebar_width": "300px",
}
project = "mex-model"
templates_path = ["."]
html_static_path = ["_static"]
html_css_files = ["custom.css"]


# Customizing json-schema conversion
# see https://sphinx-jsonschema.readthedocs.io/en/latest/extensions.html


def _patched_sphinx_jsonschema_simpletype(self, schema):  # noqa: ANN001, ANN202
    """Render the `useScheme` schema properties for every vocabulary type."""
    rows = _original_sphinx_jsonschema_simpletype(self, schema)
    if "useScheme" in schema:
        scheme = schema.pop("useScheme")
        rows.append(
            self._line(
                self._cell("useScheme"),
                self._cell(f":ref:`{scheme} <{scheme}>`"),
            )
        )
    return rows


def _patched_sphinx_jsonschema_kvpairs(self, schema, keys):  # noqa: ANN001, ANN202
    """Render `default` and `pattern` schema properties as inline code-blocks."""
    for k in keys:
        if k in schema:
            value = schema[k]
            if k in ("default", "pattern"):
                schema[k] = f"``{value}``"
    return _original_sphinx_jsonschema_kvpairs(self, schema, keys)


sjs_wide_format = importlib.import_module("sphinx-jsonschema.wide_format")
_original_sphinx_jsonschema_simpletype = sjs_wide_format.WideFormat._simpletype
sjs_wide_format.WideFormat._simpletype = _patched_sphinx_jsonschema_simpletype
_original_sphinx_jsonschema_kvpairs = sjs_wide_format.WideFormat._kvpairs
sjs_wide_format.WideFormat._kvpairs = _patched_sphinx_jsonschema_kvpairs
