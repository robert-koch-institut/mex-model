"""Migration script for splitting the model schemas into extracted and merged.

This script can be deleted after MX-2076 is merged and working as intended.
"""

import copy
import json
from pathlib import Path
from typing import Any

# Model Schema Path
SCHEMA_PATH = Path("mex/model/entities")

# The three fields to extract/separate out
EXTRACTED_ONLY_FIELDS = [
    "hadPrimarySource",
    "identifierInPrimarySource",
    "stableTargetId",
]


def ensure_dir(path: Path) -> None:
    """Create directory and its parent directories, if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def dump_schema(schema: dict[str, Any], dest_path: Path) -> None:
    """Dump schema into a JSON file."""
    with dest_path.open("w", encoding="utf-8") as f:
        json.dump(schema, f, indent=4, ensure_ascii=False)
        f.write("\n")


def split_entity_file(raw_json: str) -> None:
    """Split an entity file into extracted and merged entities."""
    # rewrite old `/schema/` path to "new" `/mex/model` path
    raw_json = raw_json.replace('"/schema/entities/', '"/mex/model/entities/merged-')
    raw_json = raw_json.replace('"/schema/', '"/mex/model/')

    # load data as json
    data: dict[str, Any] = json.loads(raw_json)
    entity_type = data["$id"].split("/")[-1]

    # remove unused target property
    data.pop("$$target", None)

    # handle concept and concept-scheme
    if "concept" in entity_type:
        concept_schema = copy.deepcopy(data)
        concept_schema["$id"] = str(data["$id"]).replace(
            "/schema/entities/", "/mex/model/entities/merged-"
        )
        dump_schema(concept_schema, SCHEMA_PATH / f"{entity_type}.json")
        return

    # Make a copy for shared/base, merged, and extracted
    shared_props = {
        k: v for k, v in data["properties"].items() if k not in EXTRACTED_ONLY_FIELDS
    }

    # Write merged schema
    merged_schema = copy.deepcopy(data)
    merged_schema.update(
        {
            "$id": str(data["$id"]).replace(
                "/schema/entities/", "/mex/model/entities/merged-"
            ),
            "properties": shared_props,
            "required": [
                req for req in data["required"] if req not in EXTRACTED_ONLY_FIELDS
            ],
            "title": "Merged " + data["title"],
        }
    )
    merged_file = SCHEMA_PATH / f"merged-{entity_type}.json"
    dump_schema(merged_schema, merged_file)

    # Write extracted schema
    extracted_schema = copy.deepcopy(data)
    extracted_schema.update(
        {
            "$$target": str(data["$$target"]).replace(
                "/schema/entities/", "mex/model/entities/extracted-"
            ),
            "$id": str(data["$id"]).replace(
                "/schema/entities/", "/mex/model/entities/extracted-"
            ),
            "title": "Extracted " + data["title"],
        }
    )
    # set type of stableTargetId to merged item identifier
    extracted_schema["properties"]["stableTargetId"]["$ref"] = extracted_schema[
        "properties"
    ]["stableTargetId"]["$ref"].replace(
        "/mex/model/fields/identifier",
        f"/mex/model/entities/merged-{extracted_schema['$id'].split('/')[-1]}#/identifier",
    )
    extracted_file = SCHEMA_PATH / f"extracted-{entity_type}.json"
    dump_schema(extracted_schema, extracted_file)


def main() -> None:
    """Split all entity files into extracted and merged entities."""
    for json_file in SCHEMA_PATH.glob("*.json"):
        if json_file.stem.startswith("extracted") or json_file.stem.startswith(
            "merged"
        ):
            continue
        with json_file.open(encoding="utf-8") as fh:
            raw_json = fh.read()
        json_file.unlink()
        split_entity_file(raw_json)
        print(f"Split: {json_file}")  # noqa: T201


if __name__ == "__main__":
    main()
