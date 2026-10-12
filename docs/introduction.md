# Introduction

The MEx model improves the **F**indability, **A**ccessibility, **I**nteroperability and **R**eusability of research data at the Robert Koch Institute in accordance to the **FAIR** data principles. Rather than providing access to research data directly, MEx captures metadata: structured descriptions of datasets, their origins, responsible teams, access conditions, and relationships to other resources.

## Purpose of the specification

The purpose of this document is threefold:
New team members (i.e. data stewards, developers, metadata specialists) need a single place to understand what the MEx model looks like, why it is structured the way it is, and how to produce valid metadata records. The [How the Model Works](how-the-model-works.md) and [Common Usage Patterns](common-usage-patterns.md) sections are the recommended starting points.

Experienced users need quick access to entity definitions, mandatory fields, vocabulary values, and mapping tables without reading prose. The sections [Entity Conventions](entity-conventions.md), [Controlled Vocabularies](controlled-vocabularies.md), and [Validation Rules](validation-rules.md) are designed for lookup rather than sequential reading.

The model exists within a broader landscape of standards such as DCAT, PROV-O, and HealthDCAT-AP, and makes deliberate choices about what to adopt, extend and leave out. The [Mappings](mappings.md) section document these choices so that anyone producing DCAT or HealthDCAT-AP mappings understands where MEx aligns and where it diverges.

## Structure of the specification

The specification is organised into the following sections:
| Section | What it covers | Audience |
| --- | --- | --- |
| [How the Model Works](how-the-model-works.md) | The Extracted/Merged entity pattern, the concept model, JSON Schema conventions, and the custom extension keywords (useScheme, sameAs, subPropertyOf). | Everyone. **Read this first!** |
| [Entity Conventions](entity-conventions.md) | Per-entity guidance: when to use each entity type, mandatory fields, common pitfalls, and example JSON instances. | Developers, Data stewards, Metadata specialists |
| [Mappings](mappings.md) — DCAT Property Mapping | The relationship between MEx and DCAT 2.0 / PROV-O: interoperability levels (A/E/P), renamed properties, omitted DCAT properties, and MEx-specific extensions. | Developers, Standards specialists |
| [Mappings](mappings.md) — HealthDCAT-AP | Background on HealthDCAT-AP and EHDS compliance, the current mapping table, gap analysis, and interim workarounds. | Developers, Standards specialists, Project leads |
| [Controlled Vocabularies](controlled-vocabularies.md) | Complete list of vocabularies, EU alignment status, and governance. | Developers, Data stewards |
| [Validation Rules](validation-rules.md) | Schema validation, vocabulary validation, cardinality rules, cross-entity validation, and obligation levels (MUST / SHOULD / MAY). | Developers, Quality assurance |
| [Common Usage Patterns](common-usage-patterns.md) | Practical guidance: describing a dataset, linking entities, modelling organisational hierarchy, handling distributions, multilingual text, and change requests. | Developers, Data stewards |
| Normative Status & Changelog | Version history and change log. | Everyone |

Sections are designed to be read independently. Cross-references point to related material where context would help, but no section assumes you have read the others. [How the Model Works](how-the-model-works.md) is the exception. This section introduces concepts used throughout the model.
