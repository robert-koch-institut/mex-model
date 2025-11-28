import json
from collections.abc import Callable, Generator
from copy import deepcopy
from importlib.resources import files
from typing import Any

__all__ = (
    "ENTITY_JSON_BY_NAME",
    "EXTRACTED_MODEL_JSON_BY_NAME",
    "FIELD_JSON_BY_NAME",
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

VOCABULARY_JSON_BY_NAME = dict(_load_json_resources("mex.model.vocabularies"))

# BW-compat for mex-invenio, can be removed after that is migrated
ENTITY_JSON_BY_NAME = deepcopy(EXTRACTED_MODEL_JSON_BY_NAME)
