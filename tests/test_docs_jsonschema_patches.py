from typing import Any
from unittest.mock import MagicMock

import jsonschema_patches
import pytest
from jsonschema_patches import (
    SUPERSEDED_GATE_IF,
    SUPERSEDED_GATE_NOTE,
    NoEscape,
    WideFormat,
    fold_superseded_gate,
    setup,
)

from mex.model import MERGED_MODEL_JSON_BY_NAME


@pytest.fixture
def renderer() -> MagicMock:
    renderer = MagicMock()
    renderer._line.side_effect = lambda *cells: list(cells)
    renderer._cell.side_effect = lambda text: text
    return renderer


def test_simpletype_links_use_scheme(
    monkeypatch: pytest.MonkeyPatch, renderer: MagicMock
) -> None:
    monkeypatch.setattr(jsonschema_patches, "_original_simpletype", lambda *_: ["row"])
    scheme = "https://mex.rki.de/item/frequency"
    schema = {"type": "string", "useScheme": scheme}

    rows = jsonschema_patches._simpletype(renderer, schema)

    assert rows == ["row", ["useScheme", f":ref:`{scheme} <{scheme}>`"]]
    assert schema == {"type": "string"}


def test_simpletype_without_use_scheme(
    monkeypatch: pytest.MonkeyPatch, renderer: MagicMock
) -> None:
    monkeypatch.setattr(jsonschema_patches, "_original_simpletype", lambda *_: ["row"])

    assert jsonschema_patches._simpletype(renderer, {"type": "string"}) == ["row"]


@pytest.mark.parametrize(
    ("schema", "expected"),
    [
        ({"default": None}, {"default": NoEscape("``null``")}),
        ({"default": []}, {"default": NoEscape("``[]``")}),
        ({"default": "Grün"}, {"default": NoEscape('``"Grün"``')}),
        ({"pattern": r"^[^\n\r]+$"}, {"pattern": NoEscape(r"``^[^\n\r]+$``")}),
        ({"format": "uri"}, {"format": "uri"}),
    ],
    ids=["null", "array", "string", "pattern", "other"],
)
def test_kvpairs_renders_verbatim_code(
    monkeypatch: pytest.MonkeyPatch, schema: dict[str, Any], expected: dict[str, Any]
) -> None:
    original = MagicMock(return_value=["row"])
    monkeypatch.setattr(jsonschema_patches, "_original_kvpairs", original)

    rows = jsonschema_patches._kvpairs(MagicMock(), schema, list(schema))

    assert rows == ["row"]
    assert schema == expected
    assert all(
        isinstance(schema[key], NoEscape)
        for key in ("default", "pattern")
        if key in schema
    )


def test_kvpairs_ignores_keys_not_requested(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(jsonschema_patches, "_original_kvpairs", MagicMock())
    schema = {"default": None}

    jsonschema_patches._kvpairs(MagicMock(), schema, ["pattern"])

    assert schema == {"default": None}


def test_noesc_marker_skips_escaping() -> None:
    # guards the assumption that sphinx-jsonschema leaves marked values untouched
    value = r"``^[^\n\r]+_*$``"
    assert WideFormat._escape(MagicMock(), NoEscape(value)) == value
    assert WideFormat._escape(MagicMock(), value) != value


def test_cell_converts_ref_roles(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(jsonschema_patches, "_original_cell", lambda _, text: [text])

    assert jsonschema_patches._cell(MagicMock(), ":ref:`a` and :ref:`b <c>`") == [
        "{ref}`a` and {ref}`b <c>`"
    ]
    assert jsonschema_patches._cell(MagicMock(), 42) == [42]


def test_setup(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("_simpletype", "_kvpairs", "_cell", "run"):
        # register the current methods, so they are restored after the test
        monkeypatch.setattr(WideFormat, name, getattr(WideFormat, name))
    app = MagicMock()

    assert setup(app) == {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
        "version": "1.0",
    }
    app.setup_extension.assert_called_once_with("sphinx-jsonschema")
    assert WideFormat._simpletype is jsonschema_patches._simpletype
    assert WideFormat._kvpairs is jsonschema_patches._kvpairs
    assert WideFormat._cell is jsonschema_patches._cell
    assert WideFormat.run is jsonschema_patches._run


def test_run_folds_superseded_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    original = MagicMock(return_value="rows")
    monkeypatch.setattr(jsonschema_patches, "_original_run", original)
    schema = {"allOf": [{"if": SUPERSEDED_GATE_IF, "then": {"required": ["foo"]}}]}
    renderer = MagicMock()

    assert jsonschema_patches._run(renderer, schema, "#/x") == "rows"
    original.assert_called_once_with(
        renderer, {"description": SUPERSEDED_GATE_NOTE, "required": ["foo"]}, "#/x"
    )


def test_fold_superseded_gate() -> None:
    other = {"required": ["baz"]}
    gate = {
        "if": SUPERSEDED_GATE_IF,
        "then": {"properties": {"foo": {"minItems": 1}}, "required": ["foo"]},
        "else": {"properties": {"foo": {"maxItems": 0}}},
    }
    schema = {
        "allOf": [gate, other],
        "description": "A dummy.",
        "properties": {"foo": {"type": "array"}},
        "required": ["identifier"],
    }

    assert fold_superseded_gate(schema) == {
        "allOf": [other],
        "description": f"A dummy.\n\n{SUPERSEDED_GATE_NOTE}",
        "properties": {"foo": {"type": "array"}},
        "required": ["foo", "identifier"],
    }
    # the original schema is left untouched
    assert schema["allOf"] == [gate, other]
    assert schema["required"] == ["identifier"]


def test_fold_superseded_gate_without_other_combinators_or_description() -> None:
    schema = {"allOf": [{"if": SUPERSEDED_GATE_IF, "then": {"required": ["foo"]}}]}

    assert fold_superseded_gate(schema) == {
        "description": SUPERSEDED_GATE_NOTE,
        "required": ["foo"],
    }


@pytest.mark.parametrize(
    "schema",
    [
        pytest.param(True, id="boolean-schema"),
        pytest.param({"required": ["foo"]}, id="no-all-of"),
        pytest.param({"allOf": [{"if": {"required": ["foo"]}}]}, id="other-if"),
    ],
)
def test_fold_superseded_gate_ignores_schemas_without_gate(schema: object) -> None:
    assert fold_superseded_gate(schema) is schema


@pytest.mark.parametrize("entity_name", sorted(MERGED_MODEL_JSON_BY_NAME))
def test_fold_superseded_gate_restores_required_fields_of_real_schemas(
    entity_name: str,
) -> None:
    schema = MERGED_MODEL_JSON_BY_NAME[entity_name]
    (gate,) = schema["allOf"]

    folded = fold_superseded_gate(schema)

    assert isinstance(folded, dict)
    assert "allOf" not in folded
    assert folded["required"] == sorted(["identifier", *gate["then"]["required"]])
