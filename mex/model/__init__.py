import json
import pkgutil
from typing import Any, Callable

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files  # type: ignore[import-not-found, no-redef]

__all__ = (
    "ENTITY_JSON_BY_NAME",
    "FIELD_JSON_BY_NAME",
    "VOCABULARY_JSON_BY_NAME",
)


def _normalize_name(name: str) -> str:
    """Normalize a filename to a valid Python identifier."""
    return name.replace("-", "_").replace(".json", "")


def _load_json_resources(
    package_name: str, file_filter: Callable[[str], bool] = lambda _: True
) -> dict[str, Any]:
    """Load JSON resources from a package with fallback for namespace packages."""
    try:
        # Primary approach using importlib.resources
        return {
            _normalize_name(f.name): json.loads(f.read_text("utf-8"))
            for f in files(package_name).iterdir()
            if f.name.endswith(".json") and file_filter(f.name)
        }
    except (TypeError, AttributeError):
        # Fallback for namespace package issues in Python 3.9
        result = {}
        module = __import__(package_name, fromlist=[""])

        for _importer, modname, _ispkg in pkgutil.iter_modules(module.__path__):
            filename = f"{modname}.json"
            if file_filter(filename):
                try:
                    resource_path = files(package_name) / filename
                    if resource_path.is_file():
                        result[_normalize_name(filename)] = json.loads(
                            resource_path.read_text("utf-8")
                        )
                except (OSError, ValueError, TypeError):
                    # Skip files that can't be read or parsed
                    continue
        return result


# Load all JSON resources with appropriate filters
ENTITY_JSON_BY_NAME = _load_json_resources(
    "mex.model.entities", lambda name: not name.startswith("concept")
)

FIELD_JSON_BY_NAME = _load_json_resources("mex.model.fields")

VOCABULARY_JSON_BY_NAME = _load_json_resources("mex.model.vocabularies")
