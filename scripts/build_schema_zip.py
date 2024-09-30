import json
from pathlib import Path
from typing import Any
from zipfile import ZipFile

REPO_ROOT = Path(__file__).parent.parent
MODEL_DIR = REPO_ROOT / "mex" / "model"


README = """\
# MEx model

JSON schema files defining the MEx metadata model.

## project

The Metadata Exchange (MEx) project is committed to improve the retrieval of RKI
research data and projects. How? By focusing on metadata: instead of providing the
actual research data directly, the MEx metadata catalog captures descriptive information
about research data and activities. On this basis, we want to make the data FAIR[^1] so
that it can be shared with others.

Via MEx, metadata will be made findable, accessible and shareable, as well as available
for further research. The goal is to get an overview of what research data is available,
understand its context, and know what needs to be considered for subsequent use.

RKI cooperated with D4L data4life gGmbH for a pilot phase where the vision of a
FAIR metadata catalog was explored and concepts and prototypes were developed.
The partnership has ended with the successful conclusion of the pilot phase.

After an internal launch, the metadata will also be made publicly available and thus be
available to external researchers as well as the interested (professional) public to
find research data from the RKI.

For further details, please consult our
[project page](https://www.rki.de/DE/Content/Forsch/MEx/MEx_node.html).

[^1]: FAIR is referencing the so-called
[FAIR data principles](https://www.go-fair.org/fair-principles/) - guidelines to make
data Findable, Accessible, Interoperable and Reusable.

**Contact** \
For more information, please feel free to email us at [mex@rki.de](mailto:mex@rki.de).

### Publisher of this document
**Robert Koch-Institut** \
Nordufer 20 \
13353 Berlin \
Germany

## package

This zip file contains the JSON schema. We defined 1.
`entities`, described by their properties, 2. `fields`, small objects, that are used as
`$ref` for certain properties, 3. an `extension`, which contains additional properties,
that are not in scope of the JSON schema definition, 4. `i18n` files, that hold
translations of the properties and are to be used in the context of user interfaces
and 5. `vocabularies`, which are used in context of the `entities`. A more detailed
description of the model's context can be found in `/docs/index.md`.

## license

This package is licensed under the [MIT license](/LICENSE). All other software
components of the MEx project are open-sourced under the same license as well.
"""


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
        for directory in ["extension", "fields", "i18n", "vocabularies"]:
            for _file in (MODEL_DIR / directory).glob("*"):
                if _file.stem in [
                    "concept-schemes",
                    "consent-status",
                    "consent-type",
                ]:
                    continue
                schema_zip.write(_file, _file.relative_to(MODEL_DIR))
        schema_zip.writestr("README.md", README)
        schema_zip.write(REPO_ROOT / "LICENSE", "LICENSE")
        schema_zip.write(REPO_ROOT / "docs" / "index.md", "docs/index.md")


if __name__ == "__main__":
    create_schema_zip()
