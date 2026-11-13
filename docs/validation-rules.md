# Validation rules

The MEx model uses JSON Schema as its primary validation mechanism. Every entity schema enforces structural constraints such as required fields, allowed types, value patterns, that can be checked automatically. This section documents what is validated, what is not, and what falls into the space between.

## Schema validation

All MEx entity schemas are written against JSON Schema Draft 2020-12. Any compliant JSON Schema validator can check an instance against the schema.

The following structural rules apply universally across all entity schemas:

### Closed content model

Every schema sets `additionalProperties: false`. An instance that includes a property not declared in the schema is invalid. This prevents silent data loss: a misspelled property name is rejected rather than quietly ignored.

### Required and optional properties

  The required array in each schema lists the properties that must be present. Optional properties have `"default": []` (arrays) or `"default": null`.

### Field type constraints

The schema enforces types at the property level:

| Constraint | Example | Enforced by |
| --- | --- | --- |
| Identifier | Alphanumeric, 14–22 characters | pattern on `/mex/model/fields/identifier` |
| Identifier in Primary source | Non-empty, no newlines, max 1000 characters | pattern on property `identifierInPrimarySource` |
| Date values | strings | patterns for different date precisions: year_month_day_time, year_month_day, year_month, year |
| Text objects | Object with value (string) and optional language (string) | `$ref` to `/mex/model/fields/text` |
| Link objects | Object with url (string) and optional metadata | `$ref` to `/mex/model/fields/link` |
| Concept URIs | URI string matching a vocabulary scheme | `$ref` to `/mex/model/entities/concept#/identifier` |

### Read-only properties

`identifier` and `stableTargetId` are marked readOnly: true. These are assigned by the system.

## Vocabulary validation

Properties that reference a controlled vocabulary declare this via the custom `useScheme` keyword in the schema:

```json
{
  "propertyName": {
    "$ref": "/mex/model/entities/concept#/identifier",
    "useScheme": "https://mex.rki.de/item/vocabulary-name"
  }
}
```

This means: the value of `propertyName` must be a valid Concept URI that belongs to the vocabulary referenced in `useScheme`.

### What validation checks

* The value must be a syntactically valid URL
* The URI must exist as a concept in the vocabulary identified by the `useScheme` URI

### What validation does not check at the schema level

JSON Schema validators do not natively understand `useScheme`, it is a custom keyword. Structural validation will confirm that the value is a string matching the concept identifier pattern, but verifying that the URI actually exists in the declared vocabulary requires an additional validation step. While MEx performs this check, standalone schema validation does not.

## Cardinality rules

MEx properties fall into two structural categories:

### Array properties

Declared as `"type": "array"` with an items definition. These accept zero or more values unless constrained by `minItems`.

| Schema declaration | Meaning |
| --- | --- |
| `"type": "array"` with `"default": []` | Optional, zero or more values |
| `"type": "array"` with `"minItems": 1` | Required, at least one value must be given |

### Single-value properties

Declared directly as a type (`string`) object (`$ref`) or via `anyOf` with a `null` alternative, when optional.

| Schema declaration | Meaning |
| --- | --- |
| `"$ref"` or `"type": "string"` and `"minLength": 1` | Required |
| `"anyOf": [{"type": null}]` with `"default": null` | Optional, one value or null |

## Cross-Entity validation

Schema validation operates on a single instance in isolation. It cannot verify that a referenced entity actually exists. Cross-entity validation is performed by the MEx backend and covers two main concerns:

### Referential integrity

Every property that references another entity (e.g. `contact`) contains a Merged identifier. The backend checks that this identifier resolves to an existing Merged item of the expected type. For example, if `contact` links to `ou-fg36-001`, there must be a `MergedOrganizationalUnit` with identifier `ou-fg36-001` in the graph.

### Provenance references

Every Extracted entity has a `hadPrimarySource` field that must reference an existing `MergedPrimarySource`. This is the foundation of MEx's provenance tracking. If the primary source does not exist, the extracted record's origin cannot be established.

### Behavior on failure

Cross-entity validation failures are not silent. The MEx backend rejects records with dangling references. The typical resolution is to ensure that referenced entities are loaded before the entities that reference them: first primary sources, then organizations and units, then resources and distributions.

## Obligation levels

The specification uses two obligation levels, following standard RFC 2119 language:

| Level | Meaning | Machine-enforceable? |
| --- | --- | --- |
| MUST | The requirement is absolute. Violating it produces an invalid record. | Yes, enforced via required, minItems, pattern, and type constraints in the schema. |
| MAY | The requirement is optional. Omitting it has no negative consequences. | No, by definition, optional requirements are not enforced. |

In practice:

* Schema validation covers all MUST requirements. If a record passes schema validation, it satisfies every absolute structural constraint.
* MAY requirements are opportunities for enrichment. Populating optional fields improves discoverability and export quality but is never required for a record to enter the catalogue.
