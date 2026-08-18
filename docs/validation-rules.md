# Validation rules

The MEx model uses JSON Schema as its primary validation mechanism. Every entity schema enforces structural constraints such as required fields, allowed types, value patterns, that can be checked automatically. This section documents what is validated, what is not, and what falls into the space between.

## Schema validation

All MEx entity schemas are written against JSON Schema Draft 2020-12. Any compliant JSON Schema validator can check an instance against the schema.

The following structural rules apply universally across all entity schemas:

### Closed content model

Every schema sets `additionalProperties: false`. An instance that includes a property not declared in the schema is invalid. This prevents silent data loss: a misspelled property name is rejected rather than quietly ignored.

### Mandatory vs optional properties

The required array in each schema lists the properties that must be present. For Extracted entities, this always includes the four system-managed fields (`identifier`, `hadPrimarySource`, `identifierInPrimarySource`, `stableTargetId`) plus any content fields that the entity cannot do without. Optional properties have either [] or null.

### Field type constraints

The schema enforces types at the property level:

| Constraint | Example | Enforced by |
| --- | --- | --- |
| Identifier format | Alphanumeric, 14–22 characters | pattern: `^[a-zA-Z0-9]{14,22}$` on the identifier field type |
| Source identifier format | Non-empty, no newlines, max 1000 characters | minLength: 1, maxLength: 1000, pattern: `^[^\\n\\r]+$` on `identifierInPrimarySource` |
| Date/time values | ISO 8601 strings | format: `date` or format: `date-time` on temporal properties with patterns for the required levels of precision |
| Text objects | Object with value (string) and optional language (string) | `$ref` to the text field `definition` |
| Link objects | Object with url (string) and optional metadata | `$ref` to the link field `definition` |
| Concept URIs | URI string matching a vocabulary scheme | `$ref` to the concept identifier type |

### Read-only properties

`identifier` and `stableTargetId` are marked readOnly: true. These are assigned by the system and must not be set by extractors or manual input. A validator may flag a write attempt to these fields, depending on the validation context.

## Vocabulary validation

Properties that reference a controlled vocabulary declare this via the custom `useScheme` keyword in the schema:

```JSON
{
  "technicalAccessibility": {
    "$ref": "/mex/model/entities/concept#/identifier",
    "useScheme": "https://mex.rki.de/item/technical-accessibility"
  }
}
```

This means: the value of `technicalAccessibility` must be a valid Concept URI that belongs to the technical-accessibility vocabulary.

### What validation checks:

* The value must be a syntactically valid URL
* The URI must exist as a concept in the vocabulary identified by the `useScheme` URI

### What validation does not check at the schema level:

JSON Schema validators do not natively understand `useScheme`, it is a custom keyword. Structural validation will confirm that the value is a string matching the concept identifier pattern, but verifying that the URI actually exists in the declared vocabulary requires an additional validation step. The MEx backend performs this check, standalone schema validation does not.

## Cardinality rules

MEx properties fall into two structural categories:

### Array properties

Declared as `type`: `array` with an items definition. These accept zero or more values unless constrained by `minItems`.

| Schema declaration | Meaning |
| --- | --- |
| `type`: `array` with no `minItems` or `default`: [] | Optional, zero or more values |
| `type`: `array` with `minItems`: 1 | Mandatory, at least one value required |

### Single-value properties

Declared directly as a type (`string`, `object`) or via `anyOf` with a null alternative. These accept exactly one value or null.

| Schema declaration | Meaning |
| --- | --- |
| `$ref`: `...` (no anyOf, no default) | Mandatory, exactly one value |
| `anyOf`: [{`$ref`: `...`}, {`type`: `null`}] with `default`: null | Optional, one value or null |

### Cardinality differences between Extracted and Merged variants

In most cases, the Extracted and Merged variants of an entity enforce the same cardinality. However, there are structural differences:

* Extracted entities always require `hadPrimarySource`, `identifierInPrimarySource`, and `stableTargetId`. Merged entities do not have these fields, they are the target of `stableTargetId`
* Merged entities may have a `supersededBy` property (optional, single-value defaults to null) that does not exist on Extracted entities.
* Where a property is mandatory on both variants, the cardinality (minItems, single-value requirement) is the same.

## Cross-Entity validation

Schema validation operates on a single instance in isolation. It cannot verify that a referenced entity actually exists. Cross-entity validation is performed by the MEx backend and covers two main concerns:

### Referential integrity

Every property that references another entity (e.g. `contact`, `distribution`, `unitInCharge`, `isPartOf`) contains a Merged identifier. The backend checks that this identifier resolves to an existing Merged entity of the expected type. For example, if unitInCharge contains `ou-fg36-001`, there must be a `MergedOrganizationalUnit` with identifier: `ou-fg36-001` in the graph.

### Provenance references

Every Extracted entity has a `hadPrimarySource` field that must reference an existing `MergedPrimarySource`. This is the foundation of MEx's provenance tracking. If the primary source does not exist, the extracted record's origin cannot be established.

### Behaviour on failure

Cross-entity validation failures are not silent. The MEx backend rejects records with dangling references. The typical resolution is to ensure that referenced entities are loaded before the entities that reference them: first primary sources, then organisations and units, then resources and distributions.

## Obligation levels

The specification uses three obligation levels, following standard RFC 2119 language:

| Level | Meaning | Machine-enforceable? |
| --- | --- | --- |
| MUST | The requirement is absolute. Violating it produces an invalid record. | Yes, enforced via required, minItems, pattern, and type constraints in the schema. |
| MAY | The requirement is optional. Omitting it has no negative consequences. | No, by definition, optional requirements are not enforced. |

In practice:

* Schema validation covers all MUST requirements. If a record passes schema validation, it satisfies every absolute structural constraint.
* SHOULD requirements are documented in the entity reference pages and in the usage patterns above. Treat them as mandatory unless you have a specific reason not to. They often reflect upcoming cardinality changes or HealthDCAT-AP alignment requirements.
* MAY requirements are opportunities for enrichment. Populating optional fields improves discoverability and export quality but is never required for a record to enter the catalogue.