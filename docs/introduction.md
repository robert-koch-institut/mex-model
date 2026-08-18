# Introduction

The Metadata Exchange model (MEx) improves the findability, accessibility, interoperability and reusability of research data at the Robert-Koch-Institute in accordance to the FAIR data principles. Rather than providing research data directly, MEx captures metadata: structured descriptions of datasets, their origins, responsible teams, access conditions, and relationships to other resources.

## Purpose of the specification

The purpose of this document is threefold:
New team members, whether they be data stewards, extractor developers, or integration partners, need a single place to understand what the MEx model looks like, why it is structured the way it is, and how to produce valid metadata records. The How the Model Works and Common Usage Patterns sections are the recommended starting points.

Experienced users need quick access to entity definitions, mandatory fields, vocabulary values, and mapping tables without reading prose. The Entity Conventions, Controlled Vocabularies, and Validation Rules sections are designed for lookup rather than sequential reading.

The model exists within a broader standards landscape of DCAT 2.0, PROV-O, and HealthDCAT-AP, and makes deliberate choices about what to adopt, extend and leave out. The Mappings sections document these choices so that anyone producing DCAT or HealthDCAT-AP exports understands where MEx aligns and where it diverges.

## Structure of the specification

The specification is organised into the following sections:

| Section | What it covers | Audience |
| --- | --- | --- |
| How the Model Works | The Extracted/Merged entity pattern, the concept model, JSON Schema conventions, and the custom extension keywords (useScheme, sameAs, subPropertyOf). | Everyone. Read this first. |
| Entity Conventions | Per-entity guidance: when to use each entity type, mandatory fields, common pitfalls, and example JSON instances. | Data stewards, extractor developers. |
| Mappings — DCAT Property Mapping | The relationship between MEx and DCAT 2.0 / PROV-O: interoperability levels (A/E/P), renamed properties, omitted DCAT properties, and MEx-specific extensions. | Integration developers, standards specialists. |
| Mappings — HealthDCAT-AP | Background on HealthDCAT-AP and EHDS compliance, the current mapping table, gap analysis, and interim workarounds. | Integration developers, project leads. |
| Controlled Vocabularies | Complete list of vocabularies, EU alignment status, and governance. | Data stewards, extractor developers. |
| Validation Rules | Schema validation, vocabulary validation, cardinality rules, cross-entity validation, and obligation levels (MUST / SHOULD / MAY). | Extractor developers, Quality Assurance. |
| Common Usage Patterns | Practical guidance: describing a dataset, linking entities, modelling organisational hierarchy, handling distributions, multilingual text, and change requests. | Data stewards, extractor developers. |
| Normative Status & Changelog | Version history and change log. | Everyone. |

Sections are designed to be read independently. Cross-references point to related material where context would help, but no section assumes you have read the others. The exception is How the Model works, which introduces concepts used throughout.