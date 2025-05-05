import json
from importlib.resources import files

ENTITIES_BY_NAME = {
    f.name.replace("-", "_"): json.loads(f.read_text("utf-8"))
    for f in files("mex.model.entities").iterdir()
    if not f.name.startswith("concept")
}
