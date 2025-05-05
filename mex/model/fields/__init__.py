import json
from importlib.resources import files

FIELDS_BY_NAME = {
    f.name: json.loads(f.read_text("utf-8"))
    for f in files("mex.model.fields").iterdir()
}
