import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
import vocabularies
from docutils import nodes
from vocabularies import (
    MExVocabulariesDirective,
    Vocabulary,
    _localized,
    load_vocabularies,
    setup,
)

ITEM = "https://mex.rki.de/item"


def write_json(path: Path, data: Any) -> None:  # noqa: ANN401
    path.write_text(json.dumps(data), "utf-8")


@pytest.fixture
def vocabulary_dir(tmp_path: Path) -> Path:
    write_json(
        tmp_path / "concept-schemes.json",
        [
            {
                "identifier": f"{ITEM}/frequency",
                "label": "Frequency vocabulary",
                "description": {"de": "Häufigkeit", "en": "How often"},
            },
            {"identifier": f"{ITEM}/api-type", "label": "Endpoint vocabulary"},
        ],
    )
    write_json(
        tmp_path / "frequency.json",
        [
            {"identifier": f"{ITEM}/frequency-10", "inScheme": f"{ITEM}/frequency"},
            {"identifier": f"{ITEM}/frequency-2", "inScheme": f"{ITEM}/frequency"},
        ],
    )
    write_json(tmp_path / "api-type.json", [{"identifier": f"{ITEM}/api-type-1"}])
    write_json(
        tmp_path / "other-thing.json",
        [{"identifier": f"{ITEM}/other-1", "inScheme": f"{ITEM}/other"}],
    )
    write_json(tmp_path / "empty.json", [])
    return tmp_path


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ({"de": "Text", "en": "text"}, "text"),
        ({"de": "Text"}, "Text"),
        ({}, ""),
        ("plain", "plain"),
        (None, ""),
    ],
)
def test_localized(value: Any, expected: str) -> None:  # noqa: ANN401
    assert _localized(value) == expected


def test_load_vocabularies(vocabulary_dir: Path) -> None:
    loaded = load_vocabularies(vocabulary_dir)

    # vocabularies are sorted by title, empty vocabularies are skipped
    assert [vocabulary.title for vocabulary in loaded] == [
        "Endpoint vocabulary",
        "Frequency vocabulary",
        "Other thing vocabulary",
    ]
    endpoint, frequency, other = loaded
    # concepts are sorted by the numeric suffix of their identifier
    assert [concept["identifier"] for concept in frequency.concepts] == [
        f"{ITEM}/frequency-2",
        f"{ITEM}/frequency-10",
    ]
    assert frequency.description == "How often"
    # without inScheme, the scheme identifier is derived from the filename
    assert endpoint.scheme_identifier == endpoint.identifier == f"{ITEM}/api-type"
    assert endpoint.description == ""
    # a mismatching inScheme is kept, so both spellings can be linked
    assert other.identifiers == {f"{ITEM}/other-thing", f"{ITEM}/other"}


def test_directive_run(monkeypatch: pytest.MonkeyPatch, vocabulary_dir: Path) -> None:
    logger = MagicMock()
    monkeypatch.setattr(vocabularies, "logger", logger)
    directive = MagicMock()
    directive.arguments = ["../vocabularies"]
    directive.env.relfn2path.return_value = ("vocabularies", str(vocabulary_dir))

    sections = MExVocabulariesDirective.run(directive)

    assert sections == [directive._section.return_value] * 3
    directive.env.note_dependency.assert_any_call(
        str(vocabulary_dir / "concept-schemes.json")
    )
    directive.env.note_dependency.assert_any_call(
        str(vocabulary_dir / "frequency.json")
    )
    # only the vocabulary with a mismatching inScheme is reported
    logger.warning.assert_called_once()
    assert logger.warning.call_args.args[1:] == (f"{ITEM}/other", "other-thing.json")


def make_vocabulary(**overrides: Any) -> Vocabulary:  # noqa: ANN401
    fields: dict[str, Any] = {
        "identifier": f"{ITEM}/frequency",
        "scheme_identifier": f"{ITEM}/frequency",
        "title": "Frequency vocabulary",
        "description": "How often",
        "concepts": [],
        "path": Path("frequency.json"),
    }
    return Vocabulary(**{**fields, **overrides})


@pytest.mark.parametrize("description", ["How often", ""])
def test_section(description: str) -> None:
    directive = MagicMock()
    directive._table.return_value = nodes.table()
    vocabulary = make_vocabulary(description=description)

    section = MExVocabulariesDirective._section(directive, vocabulary)

    assert section["names"] == ["frequency vocabulary"]
    assert section[0].astext() == "Frequency vocabulary"
    assert [type(node) for node in section[1:]] == (
        [nodes.paragraph, nodes.table] if description else [nodes.table]
    )
    directive.state.document.note_implicit_target.assert_called_once_with(
        section, section
    )
    directive._register_label.assert_called_once_with(vocabulary, section)


def test_register_label() -> None:
    directive = MagicMock()
    directive.env.docname = "controlled-vocabularies"
    directive.env.domaindata = {"std": {"labels": {}, "anonlabels": {}}}
    section = nodes.section(ids=["frequency-vocabulary"])
    vocabulary = make_vocabulary(scheme_identifier=f"{ITEM}/Frequency-Scheme")

    MExVocabulariesDirective._register_label(directive, vocabulary, section)

    std = directive.env.domaindata["std"]
    target = ("controlled-vocabularies", "frequency-vocabulary")
    assert std["labels"] == {
        f"{ITEM}/frequency": (*target, "Frequency vocabulary"),
        f"{ITEM}/frequency-scheme": (*target, "Frequency vocabulary"),
    }
    assert std["anonlabels"] == {
        f"{ITEM}/frequency": target,
        f"{ITEM}/frequency-scheme": target,
    }


def test_table() -> None:
    directive = MagicMock()
    directive.columns = MExVocabulariesDirective.columns
    directive.column_widths = MExVocabulariesDirective.column_widths
    directive._cell.side_effect = lambda text, **_: text
    vocabulary = make_vocabulary(
        concepts=[
            {
                "identifier": f"{ITEM}/frequency-1",
                "prefLabel": {"en": "triennial"},
                "definition": {"en": "Every three years."},
            }
        ]
    )

    table = MExVocabulariesDirective._table(directive, vocabulary)

    assert table == directive.state.build_table.return_value
    directive.state.build_table.assert_called_once_with(
        (
            [20, 30, 50],
            [["Label", "Identifier", "Definition"]],
            [["triennial", f"``{ITEM}/frequency-1``", "Every three years."]],
        ),
        directive.lineno,
    )


@pytest.mark.parametrize(
    ("text", "escape", "expected"),
    [
        ("a_b *c* `d` e|f \\g", True, "a\\_b \\*c\\* \\`d\\` e\\|f \\\\g"),
        ("``a_b``", False, "``a_b``"),
        ("line 1\nline 2", True, "line 1\nline 2"),
    ],
    ids=["escaped", "verbatim", "multiline"],
)
def test_cell(text: str, *, escape: bool, expected: str) -> None:
    directive = MagicMock()
    directive.lineno = 7
    directive.state.document.current_source = "controlled-vocabularies.md"

    rowspan, colspan, lineno, lines = MExVocabulariesDirective._cell(
        directive, text, escape=escape
    )

    assert (rowspan, colspan, lineno) == (0, 0, 7)
    assert "\n".join(lines) == expected
    assert lines.items == [("controlled-vocabularies.md", 7)] * len(lines)


def test_setup() -> None:
    app = MagicMock()

    assert setup(app) == {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
        "version": "1.0",
    }
    app.add_directive.assert_called_once_with(
        "mexvocabularies", MExVocabulariesDirective
    )
