# sphinx configuration

import importlib

extensions = ["sphinx-jsonschema"]
html_theme = "alabaster"
html_theme_options = {
    "extra_nav_links": {
        "Fields": "#fields",
        "• Identifier": "#identifier",
        "• Link": "#link",
        "• Text": "#text",
        "Extracted": "#extracted",
        "• ExtractedAccessPlatform": "#extracted-access-platform",
        "• ExtractedActivity": "#extracted-activity",
        "• ExtractedBibliographicResource": "#extracted-bibliographic-resource",
        "• ExtractedConsent": "#extracted-consent",
        "• ExtractedContactPoint": "#extracted-contact-point",
        "• ExtractedDistribution": "#extracted-distribution",
        "• ExtractedOrganization": "#extracted-organization",
        "• ExtractedOrganizationalUnit": "#extracted-organizational-unit",
        "• ExtractedPerson": "#extracted-person",
        "• ExtractedPrimarySource": "#extracted-primary-source",
        "• ExtractedResource": "#extracted-resource",
        "• ExtractedVariableGroup": "#extracted-variable-group",
        "• ExtractedVariable": "#extracted-variable",
        "Merged": "#merged",
        "• MergedAccessPlatform": "#merged-access-platform",
        "• MergedActivity": "#merged-activity",
        "• MergedBibliographicResource": "#merged-bibliographic-resource",
        "• MergedConsent": "#merged-consent",
        "• MergedContactPoint": "#merged-contact-point",
        "• MergedDistribution": "#merged-distribution",
        "• MergedOrganization": "#merged-organization",
        "• MergedOrganizationalUnit": "#merged-organizational-unit",
        "• MergedPerson": "#merged-person",
        "• MergedPrimarySource": "#merged-primary-source",
        "• MergedResource": "#merged-resource",
        "• MergedVariableGroup": "#merged-variable-group",
        "• MergedVariable": "#merged-variable",
        "Concepts": "#concepts",
        "• ConceptScheme": "#concept-scheme",
        "• Concept": "#concept",
        "• Vocabularies": "#vocabularies",
    },
    "page_width": "100%",
    "fixed_sidebar": "true",
    "sidebar_width": "300px",
}
project = "mex-model"
templates_path = ["."]


# Customizing json-schema conversion
# see https://sphinx-jsonschema.readthedocs.io/en/latest/extensions.html


def _patched_sphinx_jsonschema_simpletype(self, schema):  # noqa: ANN001, ANN202
    """Render the `useScheme` schema properties for every vocabulary type."""
    rows = _original_sphinx_jsonschema_simpletype(self, schema)
    if "useScheme" in schema:
        scheme = schema.pop("useScheme")
        rows.append(self._line(self._cell("useScheme"), self._cell(scheme)))
    return rows


def _patched_sphinx_jsonschema_kvpairs(self, schema, keys):  # noqa: ANN001, ANN202
    """Render `default` and `pattern` schema properties as inline code-blocks."""
    for k in keys:
        if k in schema:
            value = schema[k]
            if k in ("default", "pattern"):
                schema[k] = f"``{value}``"
    return _original_sphinx_jsonschema_kvpairs(self, schema, keys)


sjs_wide_format = importlib.import_module("sphinx-jsonschema.wide_format")
_original_sphinx_jsonschema_simpletype = sjs_wide_format.WideFormat._simpletype
sjs_wide_format.WideFormat._simpletype = _patched_sphinx_jsonschema_simpletype
_original_sphinx_jsonschema_kvpairs = sjs_wide_format.WideFormat._kvpairs
sjs_wide_format.WideFormat._kvpairs = _patched_sphinx_jsonschema_kvpairs
