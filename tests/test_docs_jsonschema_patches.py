from typing import Any
from unittest.mock import MagicMock

import jsonschema_patches
import pytest
from jsonschema_patches import NOESC, WideFormat, setup


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
        ({"default": None}, {"default": f"{NOESC}``null``"}),
        ({"default": []}, {"default": f"{NOESC}``[]``"}),
        ({"default": "Grün"}, {"default": f'{NOESC}``"Grün"``'}),
        ({"pattern": r"^[^\n\r]+$"}, {"pattern": rf"{NOESC}``^[^\n\r]+$``"}),
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


def test_kvpairs_ignores_keys_not_requested(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(jsonschema_patches, "_original_kvpairs", MagicMock())
    schema = {"default": None}

    jsonschema_patches._kvpairs(MagicMock(), schema, ["pattern"])

    assert schema == {"default": None}


def test_noesc_marker_skips_escaping() -> None:
    # guards the assumption that sphinx-jsonschema leaves marked values untouched
    value = r"``^[^\n\r]+_*$``"
    assert WideFormat._escape(MagicMock(), f"{NOESC}{value}") == value
    assert WideFormat._escape(MagicMock(), value) != value


def test_cell_converts_ref_roles(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(jsonschema_patches, "_original_cell", lambda _, text: [text])

    assert jsonschema_patches._cell(MagicMock(), ":ref:`a` and :ref:`b <c>`") == [
        "{ref}`a` and {ref}`b <c>`"
    ]
    assert jsonschema_patches._cell(MagicMock(), 42) == [42]


def test_setup(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("_simpletype", "_kvpairs", "_cell"):
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
