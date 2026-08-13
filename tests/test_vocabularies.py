from collections.abc import Iterator

from mex.model import (
    EXTRACTED_MODEL_JSON_BY_NAME,
    MERGED_MODEL_JSON_BY_NAME,
    VOCABULARY_JSON_BY_NAME,
)


def _iter_use_schemes(node: object) -> Iterator[str]:
    """Yield all `useScheme` values found anywhere in the given json structure."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "useScheme":
                yield str(value)
            else:
                yield from _iter_use_schemes(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_use_schemes(item)


def test_use_schemes_resolve_to_vocabularies() -> None:
    use_schemes = {
        use_scheme
        for schema in (
            *EXTRACTED_MODEL_JSON_BY_NAME.values(),
            *MERGED_MODEL_JSON_BY_NAME.values(),
        )
        for use_scheme in _iter_use_schemes(schema)
    }
    known_schemes = {
        # note that `inScheme` and the filename do not always agree,
        # so a vocabulary is documented under either spelling
        f"https://mex.rki.de/item/{name.replace('_', '-')}"
        for name in VOCABULARY_JSON_BY_NAME
    } | {
        str(concept["inScheme"])
        for concepts in VOCABULARY_JSON_BY_NAME.values()
        for concept in concepts
        if "inScheme" in concept
    }
    # sanity check that we are actually comparing something
    assert "https://mex.rki.de/item/theme" in use_schemes
    # every scheme referenced by an entity must have a vocabulary
    assert sorted(use_schemes - known_schemes) == []
