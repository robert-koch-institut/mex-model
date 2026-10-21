"""Sphinx extension adjusting how sphinx-jsonschema renders the MEx schemas.

sphinx-jsonschema offers no hooks to customize its tables, so this module patches a few
methods of its `WideFormat` renderer when the extension is set up:

- `useScheme` properties get a row linking to the vocabulary they draw values from
- `default` and `pattern` values are rendered verbatim as inline code
- `:ref:` roles are converted to MyST syntax, because all pages are markdown and
  sphinx-jsonschema parses its table cells with the parser of the including page
- the `supersededBy` if/then/else gate of merged schemas is folded into a note
"""

import importlib
import json
import re
from typing import Any

from sphinx.application import Sphinx

# the package name contains a dash, so it cannot be imported with a regular statement
wide_format = importlib.import_module("sphinx-jsonschema.wide_format")
WideFormat = wide_format.WideFormat
NoEscape = wide_format.NoEscape
RST_REF_PATTERN = re.compile(r":ref:`")
VERBATIM_KEYS = ("default", "pattern")
SUPERSEDED_GATE_IF = {"properties": {"supersededBy": {"type": "null"}}}
SUPERSEDED_GATE_NOTE = (
    "Fields in **bold** are required, as long as ``supersededBy`` is not set. "
    "Once ``supersededBy`` is set, the merged item is superseded and every field "
    "except ``identifier`` and ``supersededBy`` must keep its default value."
)

# keep the unpatched methods, so that setting up the extension twice is harmless
_original_simpletype = WideFormat._simpletype
_original_kvpairs = WideFormat._kvpairs
_original_cell = WideFormat._cell
_original_run = WideFormat.run


def fold_superseded_gate(schema: object) -> object:
    """Fold a merged schema's supersededBy if/then/else gate for rendering.

    `sphinx-jsonschema` only highlights fields from the top-level `required` list
    and would render the gate as a long, raw `allOf`/`if`/`then`/`else` table.
    Instead, the fields that are required on active items are highlighted again,
    the gate is dropped and its meaning is summarized in the description.
    """
    if not isinstance(schema, dict):
        return schema
    all_of = schema.get("allOf", [])
    gates = [s for s in all_of if s.get("if") == SUPERSEDED_GATE_IF]
    if not gates:
        return schema
    (gate,) = gates
    folded = {**schema, "allOf": [s for s in all_of if s is not gate]}
    if not folded["allOf"]:
        del folded["allOf"]
    folded["required"] = sorted(
        {*schema.get("required", []), *gate.get("then", {}).get("required", [])}
    )
    description = schema.get("description")
    folded["description"] = (
        f"{description}\n\n{SUPERSEDED_GATE_NOTE}"
        if description
        else SUPERSEDED_GATE_NOTE
    )
    return folded


def _simpletype(
    self: Any,  # noqa: ANN401 - WideFormat lives in a non-importable module
    schema: dict[str, Any],
) -> list[Any]:
    """Render the `useScheme` property as a link to the vocabulary."""
    rows: list[Any] = _original_simpletype(self, schema)
    if "useScheme" in schema:
        scheme = schema.pop("useScheme")
        rows.append(
            self._line(
                self._cell("useScheme"),
                self._cell(f":ref:`{scheme} <{scheme}>`"),
            )
        )
    return rows


def _kvpairs(
    self: Any,  # noqa: ANN401 - WideFormat lives in a non-importable module
    schema: dict[str, Any],
    keys: list[str],
) -> list[Any]:
    """Render `default` and `pattern` values verbatim as inline code.

    Defaults are rendered as JSON, e.g. `null` instead of `None`, and the `NoEscape`
    string type keeps sphinx-jsonschema from escaping backslashes inside the code span.
    """
    for key in VERBATIM_KEYS:
        if key in keys and key in schema:
            value = schema[key]
            code = json.dumps(value, ensure_ascii=False) if key == "default" else value
            schema[key] = NoEscape(f"``{code}``")
    rows: list[Any] = _original_kvpairs(self, schema, keys)
    return rows


def _cell(
    self: Any,  # noqa: ANN401 - WideFormat lives in a non-importable module
    text: Any,  # noqa: ANN401 - cells may hold any json value
) -> list[Any]:
    """Convert `:ref:` roles to MyST syntax, as cells are parsed as markdown."""
    if isinstance(text, str):
        text = RST_REF_PATTERN.sub("{ref}`", text)
    cell: list[Any] = _original_cell(self, text)
    return cell


def _run(
    self: Any,  # noqa: ANN401 - WideFormat lives in a non-importable module
    schema: dict[str, Any],
    pointer: str = "",
) -> Any:  # noqa: ANN401 - the return type is defined by sphinx-jsonschema
    """Render the supersededBy gate of merged schemas in a readable way."""
    return _original_run(self, fold_superseded_gate(schema), pointer)


def setup(app: Sphinx) -> dict[str, Any]:
    """Set up sphinx-jsonschema and patch its renderer."""
    app.setup_extension("sphinx-jsonschema")
    WideFormat._simpletype = _simpletype
    WideFormat._kvpairs = _kvpairs
    WideFormat._cell = _cell
    WideFormat.run = _run
    return {"parallel_read_safe": True, "parallel_write_safe": True, "version": "1.0"}
