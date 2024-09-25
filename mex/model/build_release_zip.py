import json
from pathlib import Path
from typing import Any
from zipfile import ZipFile


def create_merged_entities() -> dict[str, dict[str, Any]]:
    """Create merged models out of models in `entities` folder.

    Removes elements "hadPrimarySource", "identifierInPrimarySource", and
    "stableTargetId" from sections `properties` and `required`.
    Skips the models "concept", "concept-scheme", "consent", and "primary-source".

    Returns:
        mapping of source filenames to merged entities.
    """
    merged_entities = {}
    for extracted_model_file in (Path(__file__).parent / "entities").glob("*.json"):
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


def create_release_zip():
    """Create release.zip archive.

    The archive includes the merged entities, all vocabularies except "concept-schemes",
    "consent-status", and "consent-type", and all files from the "fields" and "i18n"
    directories.
    """
    with ZipFile("release.zip", "w") as release_zip:
        for filename, content in create_merged_entities().items():
            release_zip.writestr(
                "merged_entities/" + filename, json.dumps(content, indent=4)
            )
        for directory in ["fields", "i18n", "vocabularies"]:
            for _file in (Path(__file__).parent / directory).glob("*"):
                if _file.stem in [
                    "concept-schemes",
                    "consent-status",
                    "consent-type",
                ]:
                    continue
                release_zip.write(_file, _file.relative_to(Path(__file__).parent))


if __name__ == "__main__":
    create_release_zip()
