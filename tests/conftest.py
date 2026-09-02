import sys
from pathlib import Path

# the sphinx extensions live in `docs` and are imported by their bare module names,
# just like `conf.py` does it, so the docs folder has to be on the import path
DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
sys.path.insert(0, str(DOCS_DIR))

# schema-check helper modules live in `scripts` and are imported by their bare
# module names from the test suite, so the scripts folder has to be on the path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
