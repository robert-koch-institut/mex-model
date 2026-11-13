from pathlib import Path

import pytest
from sphinx.cmd.build import build_main

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"


@pytest.mark.integration
def test_docs_build_without_warnings(tmp_path: Path) -> None:
    warnings = tmp_path / "warnings.log"

    exit_code = build_main(
        [
            "-aE",
            "-b",
            "dirhtml",
            "-q",
            "-w",
            str(warnings),
            str(DOCS_DIR),
            str(tmp_path / "dist"),
        ]
    )

    assert exit_code == 0
    assert warnings.read_text("utf-8") == ""
