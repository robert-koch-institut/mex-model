import json
from pathlib import Path
from typing import Any
from zipfile import ZipFile

MODEL_DIR = Path(__file__).parent.parent / "mex" / "model"


def create_merged_entities() -> dict[str, dict[str, Any]]:
    """Create merged models out of models in `entities` folder.

    Removes elements "hadPrimarySource", "identifierInPrimarySource", and
    "stableTargetId" from sections `properties` and `required`.
    Skips the models "concept", "concept-scheme", "consent", and "primary-source".

    Returns:
        mapping of source filenames to merged entities.
    """
    merged_entities = {}
    for extracted_model_file in (MODEL_DIR / "entities").glob("*.json"):
        if extracted_model_file.stem in [
            "concept",
            "concept-scheme",
            "consent",
            "primary-source",
        ]:
            continue
        with extracted_model_file.open(encoding="utf8") as f:
            extracted_model = json.load(f)
        for key in ["hadPrimarySource", "identifierInPrimarySource", "stableTargetId"]:
            del extracted_model["properties"][key]
            extracted_model["required"].remove(key)
        merged_entities[extracted_model_file.name] = extracted_model
    return merged_entities


def create_schema_zip():
    """Create schema.zip archive.

    The archive includes the merged entities, all vocabularies except "concept-schemes",
    "consent-status", and "consent-type", and all files from the "fields" and "i18n"
    directories.
    """
    with ZipFile("schema.zip", "w") as schema_zip:
        for filename, content in create_merged_entities().items():
            schema_zip.writestr("entities/" + filename, json.dumps(content, indent=4))
        for directory in ["fields", "i18n", "vocabularies"]:
            for _file in (MODEL_DIR / directory).glob("*"):
                if _file.stem in [
                    "concept-schemes",
                    "consent-status",
                    "consent-type",
                ]:
                    continue
                schema_zip.write(_file, _file.relative_to(MODEL_DIR))


if __name__ == "__main__":
    create_schema_zip()
