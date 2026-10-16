import builtins
from typing import Any, NoReturn
from unittest.mock import MagicMock

import pytest
from docutils import nodes
from mex_example import (
    LINE_LENGTH,
    MExExampleDirective,
    UnsupportedEntityError,
    _format,
    _simplify,
    find_concept,
    generate_artificial,
    load_labels,
    schema_url,
    setup,
    to_json,
    to_variant,
    validate,
)
from mex_schema import MODEL_DIR

ENTITIES_DIR = MODEL_DIR / "entities"
ITEM = "https://mex.rki.de/item"


def make_directive(argument: str, **options: Any) -> MagicMock:  # noqa: ANN401
    directive = MagicMock()
    directive.arguments = [argument]
    directive.options = options
    # like sphinx, return the exception for `raise self.error(...)`, as a mock
    # with an exception class as side effect would raise it without the message
    directive.error.side_effect = lambda msg: ValueError(msg)  # noqa: PLW0108
    return directive


def test_schema_url() -> None:
    assert (
        schema_url(ENTITIES_DIR / "merged-resource.json")
        == "https://mex.rki.de/mex/model/entities/merged-resource"
    )


def test_validate_resolves_identifier_references() -> None:
    instance = {
        "identifier": "gglGQVGwZNJtqYDkW4N8jL",
        "contact": ["hJKL9mNoPqRsTuVwXyZ123"],
        "responsibleUnit": ["hJKL9mNoPqRsTuVwXyZ123"],
        "title": [{"value": "Surveillance", "language": "en"}],
        "activityType": [f"{ITEM}/activity-type-1"],
    }

    assert validate(ENTITIES_DIR / "merged-activity.json", instance) == []


def test_validate_returns_invalid_keys() -> None:
    instance = {
        "identifier": "gglGQVGwZNJtqYDkW4N8jL",
        "contact": ["not an identifier"],
        "title": [],
        "unknown": True,
    }

    assert validate(ENTITIES_DIR / "merged-activity.json", instance) == [
        "",
        "contact",
        "title",
    ]


def test_load_labels() -> None:
    labels = load_labels()

    assert labels[f"{ITEM}/language-1"] == "German"


def test_simplify() -> None:
    value = {
        "entityType": "MergedThing",
        "empty": [],
        "none": None,
        "list": [{"keep": 1, "drop": None}, 2, 3, 4],
    }

    assert _simplify(value) == {"list": [{"keep": 1}, 2]}


@pytest.mark.parametrize("variant", ["merged", "extracted"])
def test_generate_artificial(variant: str) -> None:
    instance = generate_artificial("Person", variant, 0)

    assert "entityType" not in instance
    assert validate(ENTITIES_DIR / f"{variant}-person.json", instance) == []
    assert ("hadPrimarySource" in instance) is (variant == "extracted")
    assert generate_artificial("Person", variant, 0) == instance


def test_generate_artificial_unsupported_entity() -> None:
    with pytest.raises(UnsupportedEntityError, match="Thing"):
        generate_artificial("Thing", "merged", 0)


@pytest.mark.parametrize(
    ("entity_name", "identifier", "expected"),
    [
        ("ConceptScheme", f"{ITEM}/frequency", f"{ITEM}/frequency"),
        ("Concept", f"{ITEM}/health-category-16", f"{ITEM}/health-category-16"),
        ("ConceptScheme", None, f"{ITEM}/access-restriction"),
    ],
)
def test_find_concept(entity_name: str, identifier: str | None, expected: str) -> None:
    assert find_concept(entity_name, identifier)["identifier"] == expected


def test_find_concept_unknown() -> None:
    with pytest.raises(ValueError, match="no Concept found with identifier 'foo'"):
        find_concept("Concept", "foo")


def test_format_inlines_values_that_fit() -> None:
    assert (
        _format({"b": [1, 2], "a": {}, "c": "x"}) == '{"a": {}, "b": [1, 2], "c": "x"}'
    )


def test_format_splits_long_values() -> None:
    text = "x" * LINE_LENGTH

    assert _format({"key": [text], "short": [1]}) == (
        f'{{\n  "key": [\n    "{text}"\n  ],\n  "short": [1]\n}}'
    )


def test_to_json_annotates_concepts() -> None:
    instance = {
        "identifier": f"{ITEM}/language-1",
        "language": [f"{ITEM}/language-1", f"{ITEM}/language-2"],
        "license": f"{ITEM}/license-1",
        "theme": [f"{ITEM}/unknown-1"],
    }

    assert to_json(instance) == (
        "{\n"
        f'  "identifier": "{ITEM}/language-1",\n'
        '  "language": [\n'
        f'    "{ITEM}/language-1",  // German\n'
        f'    "{ITEM}/language-2"  // English\n'
        "  ],\n"
        f'  "license": "{ITEM}/license-1",  '
        "// Creative Commons Attribution 4.0 International\n"
        f'  "theme": ["{ITEM}/unknown-1"]\n'
        "}"
    )


def test_to_variant() -> None:
    assert to_variant("extracted") == "extracted"
    with pytest.raises(ValueError, match="merged"):
        to_variant("foo")


def test_run_concept() -> None:
    directive = make_directive("Concept", identifier=f"{ITEM}/language-1")

    result = MExExampleDirective.run(directive)

    assert result == directive._render.return_value
    assert directive._render.call_args.args[0]["identifier"] == f"{ITEM}/language-1"


def test_run_unknown_concept() -> None:
    directive = make_directive("Concept", identifier="foo")

    with pytest.raises(ValueError, match="no Concept found"):
        MExExampleDirective.run(directive)


def test_run_unknown_schema() -> None:
    directive = make_directive("Acess")

    with pytest.raises(ValueError, match="no schema found for 'Acess'"):
        MExExampleDirective.run(directive)


@pytest.mark.parametrize("variant", ["merged", "extracted"])
def test_run_generates_valid_example(variant: str) -> None:
    directive = make_directive(" Person ", variant=variant, seed=0)

    MExExampleDirective.run(directive)

    directive._warn.assert_not_called()
    directive._render.assert_called_once_with(generate_artificial("Person", variant, 0))


def test_run_drops_invalid_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    instance = {"identifier": "gglGQVGwZNJtqYDkW4N8jL", "email": ["no mail"]}
    monkeypatch.setattr("mex_example.generate_artificial", lambda *_: instance)
    directive = make_directive("ContactPoint")

    MExExampleDirective.run(directive)

    directive._warn.assert_called_once_with(
        "example for %r violates %s at %s, dropping these fields",
        "ContactPoint",
        "merged-contact-point.json",
        "'email'",
    )
    directive._render.assert_called_once_with({"identifier": "gglGQVGwZNJtqYDkW4N8jL"})


def test_run_unsupported_by_mex_common(monkeypatch: pytest.MonkeyPatch) -> None:
    def generate(entity_name: str, *_: Any) -> NoReturn:  # noqa: ANN401
        raise UnsupportedEntityError(entity_name)

    monkeypatch.setattr("mex_example.generate_artificial", generate)
    directive = make_directive("Location")

    (note,) = MExExampleDirective.run(directive)

    assert isinstance(note, nodes.note)
    assert note.astext() == (
        "An example for Location will be generated here, "
        "once it is supported by mex-common."
    )
    directive._warn.assert_not_called()
    directive._render.assert_not_called()


def test_run_without_docs_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        if name.startswith("mex.artificial"):
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    directive = make_directive("Person")

    assert MExExampleDirective.run(directive) == []

    directive._warn.assert_called_once_with(
        "cannot generate example for %r, install the `docs` group", "Person"
    )


def test_warn(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = MagicMock()
    monkeypatch.setattr("mex_example.logger", logger)
    directive = make_directive("Person")

    MExExampleDirective._warn(directive, "oh no %r", "Person")

    logger.warning.assert_called_once_with(
        "oh no %r",
        "Person",
        location=directive.get_location.return_value,
        type="mex",
        subtype="example",
    )


def test_render() -> None:
    directive = make_directive("Person")

    (block,) = MExExampleDirective._render(directive, {"identifier": "abc"})

    assert isinstance(block, nodes.literal_block)
    assert block.astext() == '{"identifier": "abc"}'
    assert block["language"] == "json"
    directive.set_source_info.assert_called_once_with(block)


def test_setup() -> None:
    app = MagicMock()

    assert setup(app) == {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
        "version": "1.0",
    }
    app.add_directive.assert_called_once_with("mex-example", MExExampleDirective)
