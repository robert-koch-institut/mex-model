import json
from importlib.resources import files

__all__ = (
    "ENTITY_JSON_BY_NAME",
    "FIELD_JSON_BY_NAME",
    "VOCABULARY_JSON_BY_NAME",
)

ENTITY_JSON_BY_NAME = {
    f.name.replace("-", "_").replace(".json", ""): json.loads(f.read_text("utf-8"))
    for f in list(files("mex.model.entities").iterdir())
    if not f.name.startswith("concept")
}
FIELD_JSON_BY_NAME = {
    f.name.replace("-", "_").replace(".json", ""): json.loads(f.read_text("utf-8"))
    for f in list(files("mex.model.fields").iterdir())
}
VOCABULARY_JSON_BY_NAME = {
    f.name.replace("-", "_").replace(".json", ""): json.loads(f.read_text("utf-8"))
    for f in list(files("mex.model.vocabularies").iterdir())
}
