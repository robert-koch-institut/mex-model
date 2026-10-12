# Introduction

The Metadata Exchange model (MEx) improves the findability, accessibility, interoperability and reusability of research data at the Robert Koch Institute (RKI) in accordance with the FAIR data principles. Rather than providing research data directly, MEx captures metadata: structured descriptions of datasets, their origins, responsible teams, access conditions, and relationships to other resources.

## Purpose of the specification

The purpose of this document is threefold:
New team members, whether they be data stewards, extractor developers, or integration partners, need a single place to understand what the MEx model looks like, why it is structured the way it is, and how to produce valid metadata records. The How the model works and Common usage patterns sections are the recommended starting points.

Experienced users need quick access to entity definitions, mandatory fields, vocabulary values, and mapping tables without reading prose. The Entity conventions, Controlled vocabularies, and Validation rules sections are designed for lookup rather than sequential reading.

The model exists within a broader standards landscape of DCAT 2.0, PROV-O, and HealthDCAT-AP, and makes deliberate choices about what to adopt, extend and leave out. The Mappings section documents these choices so that anyone producing DCAT or HealthDCAT-AP exports understands where MEx aligns and where it diverges.

## Structure of the specification

The specification is organized into the following sections:

| Section | What it covers | Audience |
| --- | --- | --- |
| How the model works | The Extracted/Merged entity pattern, the concept model, JSON Schema conventions, and the custom extension keywords (useScheme, sameAs, subPropertyOf). | Everyone. Read this first. |
| Entity conventions | Per-entity guidance: when to use each entity type, mandatory fields, common pitfalls, and example JSON instances. | Data stewards, extractor developers. |
| Mappings — DCAT property mapping | The relationship between MEx and DCAT 2.0 / PROV-O: interoperability levels (A/E/P), renamed properties, omitted DCAT properties, and MEx-specific extensions. | Integration developers, standards specialists. |
| Mappings — HealthDCAT-AP | Background on HealthDCAT-AP and EHDS compliance, and how MEx approaches alignment. A mapping table and gap analysis will follow. | Integration developers, project leads. |
| Controlled vocabularies | Complete list of vocabularies, EU alignment status, and governance. | Data stewards, extractor developers. |
| Validation rules | Schema validation, vocabulary validation, cardinality rules, cross-entity validation, and obligation levels (MUST / SHOULD / MAY). | Extractor developers, Quality Assurance. |
| Common usage patterns | Practical guidance: describing a dataset, linking entities, modeling organizational hierarchy, handling distributions, multilingual text, and change requests. | Data stewards, extractor developers. |

Sections are designed to be read independently. Cross-references point to related material where context would help, but no section assumes you have read the others. The exception is How the model works, which introduces concepts used throughout.
