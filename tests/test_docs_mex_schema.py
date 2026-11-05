from pathlib import Path
from unittest.mock import MagicMock

import pytest
from mex_schema import (
    MODEL_DIR,
    MExEntityDirective,
    MExFieldDirective,
    _MExSchemaDirective,
    setup,
    to_filename,
)

DOCS_DIR = MODEL_DIR.parents[1] / "docs"
ENTITIES_DIR = MODEL_DIR / "entities"


def make_directive(argument: str, page: Path = DOCS_DIR / "page.md") -> MagicMock:
    directive = MagicMock()
    directive.arguments = [argument]
    directive.env.doc2path.return_value = page
    # like sphinx, return the exception for `raise self.error(...)`, as a mock
    # with an exception class as side effect would raise it without the message
    directive.error.side_effect = lambda msg: ValueError(msg)  # noqa: PLW0108
    return directive


@pytest.mark.parametrize(
    ("entity_name", "expected"),
    [
        ("Resource", "resource"),
        ("AccessPlatform", "access-platform"),
        ("OrganizationalUnit", "organizational-unit"),
    ],
)
def test_to_filename(entity_name: str, expected: str) -> None:
    assert to_filename(entity_name) == expected


def test_entity_run_renders_both_variants() -> None:
    directive = make_directive(" AccessPlatform ")

    MExEntityDirective.run(directive)

    directive._render.assert_called_once_with(
        [
            ENTITIES_DIR / "extracted-access-platform.json",
            ENTITIES_DIR / "merged-access-platform.json",
        ]
    )


def test_entity_run_renders_single_schema() -> None:
    directive = make_directive("ConceptScheme")

    MExEntityDirective.run(directive)

    directive._render.assert_called_once_with([ENTITIES_DIR / "concept-scheme.json"])


def test_field_run() -> None:
    directive = make_directive("Identifier")

    MExFieldDirective.run(directive)

    directive._render.assert_called_once_with([MODEL_DIR / "fields/identifier.json"])


@pytest.mark.parametrize(
    ("page", "prefix"),
    [
        (DOCS_DIR / "page.md", "../mex/model"),
        (DOCS_DIR / "nested" / "page.md", "../../mex/model"),
    ],
    ids=["top-level", "nested"],
)
def test_render_relative_to_page(page: Path, prefix: str) -> None:
    directive = make_directive("Concept", page)

    parsed_nodes = _MExSchemaDirective._render(
        directive,
        [ENTITIES_DIR / "concept.json", MODEL_DIR / "fields/text.json"],
    )

    assert parsed_nodes == directive.parse_text_to_nodes.return_value
    assert directive.parse_text_to_nodes.call_args.args[0] == (
        f"```{{jsonschema}} {Path(prefix, 'entities/concept.json')}\n"
        ":encoding: utf8\n"
        "```\n"
        "\n"
        f"```{{jsonschema}} {Path(prefix, 'fields/text.json')}\n"
        ":encoding: utf8\n"
        "```\n"
    )


def test_render_unknown_schema() -> None:
    directive = make_directive("Acess")

    with pytest.raises(ValueError, match="no schema found for 'Acess'"):
        _MExSchemaDirective._render(directive, [ENTITIES_DIR / "acess.json"])

    directive.parse_text_to_nodes.assert_not_called()


def test_setup() -> None:
    app = MagicMock()

    assert setup(app) == {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
        "version": "1.0",
    }
    app.setup_extension.assert_called_once_with("jsonschema_patches")
    app.add_directive.assert_any_call("mex-entity", MExEntityDirective)
    app.add_directive.assert_any_call("mex-field", MExFieldDirective)
