import json
from collections.abc import Callable, Generator
from copy import deepcopy
from importlib.resources import files
from typing import Any

__all__ = (
    "ENTITY_JSON_BY_NAME",
    "EXTRACTED_MODEL_JSON_BY_NAME",
    "FIELD_JSON_BY_NAME",
    "I18N_PO_DATA_BY_LANGUAGE",
    "MERGED_MODEL_JSON_BY_NAME",
    "VOCABULARY_JSON_BY_NAME",
)


def _normalize_name(name: str) -> str:
    """Normalize a filename to a valid Python identifier."""
    return name.replace("-", "_").replace(".json", "")


def _load_json_resources(
    package_name: str, file_filter: Callable[[str], bool] = lambda _: True
) -> Generator[tuple[str, Any]]:
    """Load JSON resources from a package with fallback for namespace packages."""
    # Primary approach using importlib.resources
    for file in files(package_name).iterdir():
        if file.name.endswith(".json") and file_filter(file.name):
            yield _normalize_name(file.name), json.loads(file.read_text("utf-8"))


def _load_po_resources(package_name: str) -> Generator[tuple[str, str]]:
    """Load the raw contents of gettext portable object files from a package."""
    for file in files(package_name).iterdir():
        if file.name.endswith(".po"):
            yield file.name.removesuffix(".po"), file.read_text("utf-8")


# Load all JSON resources with appropriate filters
EXTRACTED_MODEL_JSON_BY_NAME = {
    name.removeprefix("extracted_"): schema
    for name, schema in _load_json_resources(
        "mex.model.entities", lambda name: name.startswith("extracted")
    )
}

MERGED_MODEL_JSON_BY_NAME = {
    name.removeprefix("merged_"): schema
    for name, schema in _load_json_resources(
        "mex.model.entities", lambda name: name.startswith("merged")
    )
}

FIELD_JSON_BY_NAME = dict(_load_json_resources("mex.model.fields"))

VOCABULARY_JSON_BY_NAME = dict(
    _load_json_resources(
        # concept-schemes is a scheme registry, not a vocabulary
        "mex.model.vocabularies",
        lambda name: name != "concept-schemes.json",
    )
)

I18N_PO_DATA_BY_LANGUAGE = dict(_load_po_resources("mex.model.i18n"))

# BW-compat for mex-invenio, can be removed after that is migrated
ENTITY_JSON_BY_NAME = deepcopy(EXTRACTED_MODEL_JSON_BY_NAME)
