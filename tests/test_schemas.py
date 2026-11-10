import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from schemas import (
    SUPERSEDED_GATE_IF,
    SUPERSEDED_GATE_NOTE,
    MExSchemasDirective,
    Schema,
    fold_superseded_gate,
    load_schemas,
    setup,
)

from mex.model import MERGED_MODEL_JSON_BY_NAME


def test_schema_titles() -> None:
    schema = Schema(title="Extracted Access Platform", path=Path("dummy.json"))
    assert schema.anchor == "extracted-access-platform"
    assert schema.nav_title == "ExtractedAccessPlatform"


def test_load_schemas(tmp_path: Path) -> None:
    (tmp_path / "beta.json").write_text(json.dumps({"title": "Beta"}), "utf-8")
    (tmp_path / "alpha.json").write_text(json.dumps({}), "utf-8")
    (tmp_path / "gamma.txt").write_text("not a schema", "utf-8")

    # schemas are sorted by path and fall back to the filename as title
    assert load_schemas(tmp_path) == [
        Schema(title="alpha", path=tmp_path / "alpha.json"),
        Schema(title="Beta", path=tmp_path / "beta.json"),
    ]
    # only files matching the pattern are loaded
    assert load_schemas(tmp_path, "b*.json") == [
        Schema(title="Beta", path=tmp_path / "beta.json"),
    ]


def test_directive_run(tmp_path: Path) -> None:
    (tmp_path / "beta.json").write_text(json.dumps({"title": "Beta"}), "utf-8")
    (tmp_path / "alpha.json").write_text(json.dumps({"title": "Alpha"}), "utf-8")
    directive = MagicMock()
    directive.arguments = ["../schemas", "b*.json"]
    directive.env.relfn2path.return_value = ("schemas", str(tmp_path))

    parsed_nodes = MExSchemasDirective.run(directive)

    assert parsed_nodes == directive.parse_text_to_nodes.return_value
    directive.env.relfn2path.assert_called_once_with("../schemas")
    # only the matching schema is rendered and registered as a dependency
    directive.env.note_dependency.assert_called_once_with(str(tmp_path / "beta.json"))
    assert directive.parse_text_to_nodes.call_args.args[0] == (
        f".. jsonschema:: {tmp_path / 'beta.json'}\n    :encoding: utf8\n"
    )


def test_setup() -> None:
    app = MagicMock()

    assert setup(app) == {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
        "version": "1.0",
    }
    app.setup_extension.assert_called_once_with("sphinx-jsonschema")
    app.add_directive.assert_called_once_with("mexschemas", MExSchemasDirective)


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
