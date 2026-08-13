import json
from pathlib import Path

from navigation import build_nav_links

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

INDEX = """\
MEx Metadata Schema
===================

Some introduction that is not a section.

Fields
------

.. mexschemas:: schemas b*.json

Vocabularies
^^^^^^^^^^^^

.. mexvocabularies:: vocabularies
"""


def test_build_nav_links(tmp_path: Path) -> None:
    (tmp_path / "index.rst").write_text(INDEX, "utf-8")
    schemas = tmp_path / "schemas"
    schemas.mkdir()
    (schemas / "alpha.json").write_text(json.dumps({"title": "Alpha"}), "utf-8")
    (schemas / "beta.json").write_text(json.dumps({"title": "Extracted Beta"}), "utf-8")
    vocabularies = tmp_path / "vocabularies"
    vocabularies.mkdir()
    (vocabularies / "concept-schemes.json").write_text(
        json.dumps(
            [
                {
                    "identifier": "https://mex.rki.de/item/api-type",
                    "label": "Api type vocabulary",
                }
            ]
        ),
        "utf-8",
    )
    (vocabularies / "api-type.json").write_text(
        json.dumps([{"identifier": "https://mex.rki.de/item/api-type-1"}]), "utf-8"
    )

    assert build_nav_links(tmp_path / "index.rst") == {
        # the document title is skipped, because the theme's logo links to it
        "Fields": "#fields",
        # only the schema matching the directive's pattern is listed
        "• ExtractedBeta": "#extracted-beta",
        "• Vocabularies": "#vocabularies",
        "◦ Api type": "#api-type-vocabulary",
    }


def test_build_nav_links_of_docs_index() -> None:
    links = build_nav_links(DOCS_DIR / "index.rst")

    # spot check one entry of each kind against the real documentation
    assert links["Fields"] == "#fields"
    assert links["• ExtractedResource"] == "#extracted-resource"
    assert links["◦ Theme"] == "#theme-vocabulary"
