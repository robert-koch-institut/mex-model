"""Sphinx configuration for MEx model specification."""

import sys
from pathlib import Path

# Make the _ext directory importable
sys.path.insert(0, str(Path(__file__).parent / "_ext"))

# --- Extensions -----------------------------------------------------------

extensions = [
    "myst_parser",  # parse .md files
    "jsonschema_patches",  # render JSON schemas as tables, adjusted for MEx
    "vocabularies",  # directive: mexvocabularies
    "mex_schema",  # directives: {mex-entity}, {mex-field}
]

# --- MyST-Parser settings -------------------------------------------------

myst_enable_extensions = [
    "colon_fence",  # ::: directive syntax
    "fieldlist",  # field lists in MD
    "deflist",  # definition lists in MD
]

# Generate slug anchors for h1-h3 so `[text](#heading-slug)` links resolve
myst_heading_anchors = 3

# All pages are written in markdown
source_suffix = {".md": "markdown"}

# --- Project metadata ------------------------------------------------------

project = "mex-model"

# --- HTML output settings --------------------------------------------------

html_theme = "alabaster"
html_theme_options = {
    "page_width": "100%",
    "fixed_sidebar": "true",
    "sidebar_width": "300px",
}
templates_path = ["."]
html_static_path = ["_static"]
html_css_files = ["custom.css"]
