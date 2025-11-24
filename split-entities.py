import json
from pathlib import Path
from typing import Any

# Paths (adjust as needed)
SRC_DIR = Path("mex/model/entities")
BASE_DIR = Path("mex/model/base-entities")
MERGED_DIR = Path("mex/model/merged-entities")
EXTRACTED_DIR = Path("mex/model/extracted-entities")

# The three fields to extract/separate out
EXTRACT_ONLY_FIELDS = [
    "hadPrimarySource",
    "identifierInPrimarySource",
    "stableTargetId",
]


def ensure_dir(path: Path) -> None:
    """Create directory and its parent directories, if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def split_entity_file(src_path: Path) -> None:
    """Split an entity file into extracted and merged entities."""
    with src_path.open(encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)

    # Make a copy for shared/base, merged, and extracted
    base_props = {
        k: v for k, v in data["properties"].items() if k not in EXTRACT_ONLY_FIELDS
    }
    extracted_only_props = {
        k: v for k, v in data["properties"].items() if k in EXTRACT_ONLY_FIELDS
    }

    # Write base schema
    base_schema = dict(data)
    base_schema["properties"] = base_props
    base_schema["title"] = "Base Entity: " + base_schema.get("title", src_path.stem)
    base_file = BASE_DIR / f"base-{src_path.stem}"
    with base_file.open("w", encoding="utf-8") as f:
        json.dump(base_schema, f, indent=2, ensure_ascii=False)

    # Write merged schema
    merged_schema = {
        "$schema": data.get("$schema", "http://json-schema.org/draft/2020-12/schema"),
        "$id": data.get("$id", "") + "-merged",
        "title": (data.get("title", src_path.stem) + " (Merged)"),
        "allOf": [{"$ref": f"/schema/base-entities/base-{src_path.stem}"}],
        "description": data.get("description", ""),
        "type": "object",
        "required": [
            req for req in data.get("required", []) if req not in EXTRACT_ONLY_FIELDS
        ],
        # properties technically not needed with allOf, but can include extension here
    }
    merged_file = MERGED_DIR / f"merged-{src_path.stem}.json"
    with merged_file.open("w", encoding="utf-8") as f:
        json.dump(merged_schema, f, indent=2, ensure_ascii=False)

    # Write extracted schema
    extracted_schema = {
        "$schema": data.get("$schema", "http://json-schema.org/draft/2020-12/schema"),
        "$id": data.get("$id", "") + "-extracted",
        "title": (data.get("title", src_path.stem) + " (Extracted)"),
        "allOf": [{"$ref": f"/schema/base-entities/base-{src_path.stem}"}],
        "description": "Extracted fields for: " + data.get("title", src_path.stem),
        "type": "object",
        "properties": extracted_only_props,
        "required": data.get("required", []),
    }
    extracted_file = EXTRACTED_DIR / f"extracted-{src_path.stem}.json"
    with extracted_file.open("w", encoding="utf-8") as f:
        json.dump(extracted_schema, f, indent=2, ensure_ascii=False)


def main() -> None:
    """Split all entity files into extracted and merged entities."""
    ensure_dir(BASE_DIR)
    ensure_dir(MERGED_DIR)
    ensure_dir(EXTRACTED_DIR)

    for json_file in SRC_DIR.glob("*.json"):
        split_entity_file(json_file)
        print(f"Split: {json_file}")  # noqa: T201


if __name__ == "__main__":
    main()
