import json
from pathlib import Path
from typing import Any

# Paths (adjust as needed)
SRC_DIR = Path("mex/model/entities")
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


def dump_schema(schema: dict[str, Any], dest_path: Path) -> None:
    """Dump schema into a JSON file."""
    with dest_path.open("w", encoding="utf-8") as f:
        json.dump(schema, f, indent=4, ensure_ascii=False)
        f.write("\n")


def split_entity_file(src_path: Path) -> None:
    """Split an entity file into extracted and merged entities."""
    with src_path.open(encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)

    # Make a copy for shared/base, merged, and extracted
    shared_props = {
        k: v for k, v in data["properties"].items() if k not in EXTRACT_ONLY_FIELDS
    }

    # Write merged schema
    merged_schema: dict[str, Any] = json.loads(json.dumps(data))  # create deep copy
    # remove target because I think that merged items do not have a target since they
    # are the target themselves
    merged_schema.pop("$$target")
    merged_schema.update(
        {
            "properties": shared_props,
            "required": [
                req for req in data["required"] if req not in EXTRACT_ONLY_FIELDS
            ],
        }
    )
    merged_file = MERGED_DIR / f"{src_path.stem}.json"
    dump_schema(merged_schema, merged_file)

    # Write extracted schema
    description = "Extracted entities represent data from a single primary source."
    if "description" in data:
        description += " " + data["description"]
    extracted_schema: dict[str, Any] = json.loads(json.dumps(data))  # create deep copy
    extracted_schema.update(
        {
            "$id": str(data["$id"]).replace(
                "https://mex.rki.de/schema/entities/",
                "https://mex.rki.de/schema/extracted-entities/extracted-",
            ),
            "description": description,
            "title": "Extracted " + data["title"],
        }
    )
    extracted_file = EXTRACTED_DIR / f"extracted-{src_path.stem}.json"
    dump_schema(extracted_schema, extracted_file)


def main() -> None:
    """Split all entity files into extracted and merged entities."""
    ensure_dir(MERGED_DIR)
    ensure_dir(EXTRACTED_DIR)

    for json_file in SRC_DIR.glob("*.json"):
        split_entity_file(json_file)
        print(f"Split: {json_file}")  # noqa: T201


if __name__ == "__main__":
    main()
