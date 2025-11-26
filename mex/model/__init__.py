import json
import pkgutil
from collections.abc import Generator
from copy import deepcopy
from typing import Any, Callable

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files  # type: ignore[import-not-found, no-redef]

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
) -> Generator[tuple[str, dict[str, Any]]]:
    """Load JSON resources from a package with fallback for namespace packages."""
    try:
        # Primary approach using importlib.resources
        for file in files(package_name).iterdir():
            if file.name.endswith(".json") and file_filter(file.name):
                yield _normalize_name(file.name), json.loads(file.read_text("utf-8"))
    except (TypeError, AttributeError):
        # Fallback for namespace package issues in Python 3.9
        module = __import__(package_name, fromlist=[""])
        for _, name, _ in pkgutil.iter_modules(module.__path__):
            filename = f"{name}.json"
            if file_filter(filename):
                try:
                    resource_path = files(package_name) / filename
                    if resource_path.is_file():
                        yield (
                            _normalize_name(filename),
                            json.loads(resource_path.read_text("utf-8")),
                        )
                except (OSError, ValueError, TypeError):
                    # Skip files that can't be read or parsed
                    continue


# Load all JSON resources with appropriate filters
EXTRACTED_MODEL_JSON_BY_NAME = {
    name.removeprefix("extracted-"): schema
    for name, schema in _load_json_resources(
        "mex.model.entities", lambda name: name.startswith("extracted")
    )
}

MERGED_MODEL_JSON_BY_NAME = {
    name.removeprefix("merged-"): schema
    for name, schema in _load_json_resources(
        "mex.model.entities", lambda name: name.startswith("merged")
    )
}

FIELD_JSON_BY_NAME = dict(_load_json_resources("mex.model.fields"))

VOCABULARY_JSON_BY_NAME = dict(_load_json_resources("mex.model.vocabularies"))

# BW-compat for mex-invenio, can be removed after that is migrated
ENTITY_JSON_BY_NAME = deepcopy(EXTRACTED_MODEL_JSON_BY_NAME)
